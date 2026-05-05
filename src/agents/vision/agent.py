"""Vision Agent — CNN-based medical image analysis.

Uses ResNet-50 (or fine-tuned variant) to detect anomalies, tumors, and
pathologies in X-rays, MRIs, and other medical scans.
"""

from typing import Any, Optional
import torch
import torch.nn as nn
from torchvision import models
from PIL import Image

from src.agents.base import BaseAgent
from src.data.preprocessing.image_preprocessor import ImagePreprocessor
from config import settings


class VisionAgent(BaseAgent):
    """Medical image analysis agent using ResNet-50."""

    name = "vision_agent"
    description = "CNN / ResNet — Tumor / anomaly detection from medical images"

    DISEASE_CLASSES = [
        "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration",
        "Mass", "Nodule", "Pneumonia", "Pneumothorax",
        "Consolidation", "Edema", "Emphysema", "Fibrosis",
        "Pleural_Thickening", "Hernia", "Normal",
    ]

    def __init__(self, model_path: Optional[str] = None):
        super().__init__()
        self.preprocessor = ImagePreprocessor()
        self._model_path = model_path or settings.vision_model_path
        self._model = None
        self._model_loaded = False
        self._load_attempted = False
        # Don't load ResNet at init — lazy load on first use
        self.log("info", f"Vision agent initialized — model: {settings.vision_model_name}")

    def _load_model(self) -> nn.Module:
        """Load ResNet-50 model. Called lazily on first use."""
        if self._load_attempted:
            return self._model
        
        self._load_attempted = True
        
        model = models.resnet50(weights=None)
        model.fc = nn.Linear(model.fc.in_features, settings.num_disease_classes)
        try:
            state_dict = torch.load(self._model_path, map_location="cpu", weights_only=True)
            model.load_state_dict(state_dict)
            self._model_loaded = True
            self.log("info", f"Loaded trained model from {self._model_path}")
        except FileNotFoundError:
            self._load_error = f"Model file not found: {self._model_path}"
            self.log("warning", "No trained model found — using untrained weights for now")
        except Exception as e:
            self._load_error = str(e)
            self.log("warning", f"Failed to load model, using untrained weights: {e}")
        
        model.eval()
        self._model = model
        return model

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
                return {"error": f"Failed to load image: {e}", "findings": [], "confidence": 0.0}

        if not image:
            return {"error": "No image provided", "findings": [], "confidence": 0.0}

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

            return {
                "findings": findings,
                "total_detected": len(findings),
                "highest_confidence": findings[0]["confidence"] if findings else 0.0,
                "anomalies": [f["condition"] for f in findings],
                "agent": self.name,
            }
        except Exception as e:
            self.log("error", f"Image analysis failed: {e}")
            return {"error": str(e), "findings": [], "confidence": 0.0}
