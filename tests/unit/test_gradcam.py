"""Unit tests for Grad-CAM explainability engine."""

import numpy as np
import torch
from PIL import Image

from src.agents.vision.agent import VisionAgent
from src.agents.vision.gradcam import GradCAM


class TestGradCAM:
    """Test gradient-weighted class activation mapping implementation."""

    def test_gradcam_computes_normalized_heatmap(self):
        """Grad-CAM must produce a (224, 224) float32 heatmap bounded in [0, 1]."""
        agent = VisionAgent()
        model = agent.model
        cam_engine = GradCAM(model)

        dummy_img = Image.new("RGB", (224, 224), color=(100, 100, 100))
        tensor = torch.tensor(agent.preprocessor.preprocess_for_model(dummy_img)).unsqueeze(0)

        cam, target_cls, confidence = cam_engine.generate_cam(tensor)

        assert isinstance(cam, np.ndarray)
        assert cam.shape == (224, 224)
        assert cam.dtype == np.float32
        assert cam.min() >= 0.0
        assert cam.max() <= 1.0
        assert 0 <= target_cls < len(agent.DISEASE_CLASSES)
        assert 0.0 <= confidence <= 1.0

        cam_engine.remove_hooks()

    def test_gradcam_overlay_generates_valid_data_uri(self):
        """Overlay helper must return a base64-encoded PNG data URI."""
        agent = VisionAgent()
        model = agent.model
        cam_engine = GradCAM(model)

        dummy_img = Image.new("RGB", (224, 224), color=(150, 150, 150))
        tensor = torch.tensor(agent.preprocessor.preprocess_for_model(dummy_img)).unsqueeze(0)
        cam, _, _ = cam_engine.generate_cam(tensor)

        data_uri = cam_engine.overlay_heatmap(dummy_img, cam, alpha=0.45)

        assert isinstance(data_uri, str)
        assert data_uri.startswith("data:image/png;base64,")
        assert len(data_uri) > 100

        cam_engine.remove_hooks()

    def test_vision_agent_run_returns_heatmap_keys(self):
        """VisionAgent.run() must include heatmap fields in its result dictionary."""
        agent = VisionAgent()
        dummy_img = Image.new("RGB", (224, 224), color=(80, 80, 80))

        import asyncio
        result = asyncio.run(agent.run({"image": dummy_img}))

        assert "heatmap" in result
        assert "heatmap_class" in result
        assert "heatmap_confidence" in result
        assert result["heatmap"] is not None
        assert result["heatmap"].startswith("data:image/png;base64,")
        assert result["heatmap_class"] in agent.DISEASE_CLASSES
