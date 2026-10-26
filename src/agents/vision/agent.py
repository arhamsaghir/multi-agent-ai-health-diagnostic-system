"""Vision Agent — CNN-based medical image analysis.

Uses a fine-tuned ResNet (architecture auto-detected from the training
checkpoint) to detect anomalies, tumors, and pathologies in X-rays, MRIs,
and other medical scans.
"""

from typing import Any, Optional
import torch
import torch.nn as nn
from torchvision import models
from PIL import Image
from loguru import logger

from src.agents.base import BaseAgent
from src.data.preprocessing.image_preprocessor import ImagePreprocessor
from src.agents.vision.gradcam import GradCAM
from src.utils.model_cache import model_cache
from config import settings


# Module-level load status shared by all VisionAgent instances so the model
# is built once per process and reused across requests (via model_cache).
_MODEL_CACHE_KEY = "vision_disease_classifier"
_MODEL_LOAD_STATUS: dict = {"arch": settings.vision_model_name, "loaded": False, "error": None}


def _load_vision_model() -> nn.Module:
    """Build the disease-classification model from the training checkpoint.

    The exported checkpoint may be a ResNet-18 or ResNet-50 variant, so the
    architecture is detected from the fc weight shape (512 vs 2048 input
    features). Without this, load_state_dict fails silently and the API
    would serve an untrained, randomly-initialized network.
    """
    state_dict = None
    arch = settings.vision_model_name
    arch_note = "no checkpoint file"

    try:
        state_dict = torch.load(settings.vision_model_path, map_location="cpu", weights_only=True)
        fc_in_features = state_dict["fc.weight"].shape[1]
        arch = "resnet18" if fc_in_features == 512 else "resnet50"
        arch_note = f"detected {arch} checkpoint (fc input dim {fc_in_features})"
    except FileNotFoundError:
        pass
    except Exception as e:
        arch_note = f"checkpoint unreadable ({e})"
        _MODEL_LOAD_STATUS["error"] = arch_note

    builder = {"resnet18": models.resnet18, "resnet50": models.resnet50}.get(arch, models.resnet50)
    model = builder(weights=None)
    model.fc = nn.Linear(model.fc.in_features, settings.num_disease_classes)

    loaded = False
    if state_dict is not None:
        try:
            model.load_state_dict(state_dict)
            loaded = True
        except Exception as e:
            _MODEL_LOAD_STATUS["error"] = f"State dict load failed: {e}"

    _MODEL_LOAD_STATUS.update({"arch": arch, "loaded": loaded})
    model.eval()

    logger.info(f"[vision_agent] Model built — arch: {arch}, {arch_note}, trained weights applied: {loaded}")
    if not loaded:
        logger.warning("[vision_agent] Serving untrained weights — predictions are not meaningful")

    return model


def get_shared_vision_model() -> nn.Module:
    """Return the process-wide shared vision model (lazy-loaded, cached)."""
    if _MODEL_CACHE_KEY not in model_cache.get_status()["registered_models"]:
        model_cache.register(_MODEL_CACHE_KEY, _load_vision_model)
    return model_cache.get(_MODEL_CACHE_KEY)


class VisionAgent(BaseAgent):
    """Medical image analysis agent using a fine-tuned ResNet."""

    name = "vision_agent"
    description = "CNN / ResNet — Chest X-ray anomaly classification across 15 classes"

    DISEASE_CLASSES = [
        "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration",
        "Mass", "Nodule", "Pneumonia", "Pneumothorax",
        "Consolidation", "Edema", "Emphysema", "Fibrosis",
        "Pleural_Thickening", "Hernia", "No Finding",
    ]

    def __init__(self, model_path: Optional[str] = None):
        super().__init__()
        self.preprocessor = ImagePreprocessor()
        self._model_path = model_path or settings.vision_model_path
        self._model = None
        self._model_loaded = False
        self._load_attempted = False
        # Don't load the network at init — lazy load on first use
        self.log("info", f"Vision agent initialized — model: {settings.vision_model_name}")

    def _load_model(self) -> nn.Module:
        """Load the shared model (cached across requests). Called lazily."""
        if self._load_attempted:
            return self._model

        self._load_attempted = True
        try:
            self._model = get_shared_vision_model()
            self._model_loaded = _MODEL_LOAD_STATUS.get("loaded", False)
            self._load_error = _MODEL_LOAD_STATUS.get("error")
        except Exception as e:
            self._load_error = str(e)
            self.log("warning", f"Failed to load shared vision model: {e}")

        return self._model

    @property
    def model(self) -> nn.Module:
        """Lazy-load model on first access."""
        return self._load_model()

    async def run(self, input_data: dict) -> dict:
        """Analyze a medical image and return findings.

        Args:
            input_data: Dict with 'image_path' or 'image' (PIL Image).

        Returns:
            Dict with findings, confidence scores, and detected anomalies.
        """
        image_path = input_data.get("image_path")
        image = input_data.get("image")

        if image_path and not image:
            try:
                image = Image.open(image_path).convert("RGB")
            except Exception as e:
                return self._error_result(f"Failed to load image: {e}")

        if not image:
            return self._error_result("No image provided")

        try:
            input_tensor = self.preprocessor.preprocess_for_model(image)
            input_tensor = torch.tensor(input_tensor).unsqueeze(0)

            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = torch.sigmoid(outputs).squeeze().tolist()

            # Build results
            if isinstance(probabilities, float):
                probabilities = [probabilities]

            findings = []
            for cls_name, prob in zip(self.DISEASE_CLASSES, probabilities):
                if prob > 0.5:
                    findings.append({
                        "condition": cls_name,
                        "confidence": round(prob, 3),
                        "severity": "high" if prob > 0.8 else "moderate" if prob > 0.6 else "low",
                    })

            findings.sort(key=lambda x: x["confidence"], reverse=True)

            # Generate Grad-CAM explainability heatmap for the most salient class
            heatmap_uri = None
            heatmap_class = None
            heatmap_confidence = 0.0

            try:
                # If there are positive findings, use top finding; otherwise argmax logit
                target_idx = None
                if findings:
                    target_name = findings[0]["condition"]
                    if target_name in self.DISEASE_CLASSES:
                        target_idx = self.DISEASE_CLASSES.index(target_name)

                cam_engine = GradCAM(self.model)
                cam, target_idx, heatmap_confidence = cam_engine.generate_cam(input_tensor, target_class=target_idx)
                heatmap_class = self.DISEASE_CLASSES[target_idx] if target_idx < len(self.DISEASE_CLASSES) else "Anomaly"
                heatmap_uri = cam_engine.overlay_heatmap(image, cam, alpha=0.45)
                cam_engine.remove_hooks()
            except Exception as cam_err:
                self.log("warning", f"Grad-CAM generation failed: {cam_err}")

            return {
                "findings": findings,
                "total_detected": len(findings),
                "highest_confidence": findings[0]["confidence"] if findings else 0.0,
                "anomalies": [f["condition"] for f in findings],
                "heatmap": heatmap_uri,
                "heatmap_class": heatmap_class,
                "heatmap_confidence": round(heatmap_confidence, 3),
                "agent": self.name,
            }
        except Exception as e:
            self.log("error", f"Image analysis failed: {e}")
            return self._error_result(str(e))

    @staticmethod
    def _error_result(message: str) -> dict:
        """Error payload that satisfies the VisionResponse contract."""
        return {
            "error": message,
            "findings": [],
            "total_detected": 0,
            "highest_confidence": 0.0,
            "anomalies": [],
            "heatmap": None,
            "heatmap_class": None,
            "heatmap_confidence": 0.0,
        }
