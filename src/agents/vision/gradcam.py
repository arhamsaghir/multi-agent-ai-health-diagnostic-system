"""Gradient-weighted Class Activation Mapping (Grad-CAM) for medical vision models.

Provides spatial explainability heatmaps for convolutional backbones (e.g.
ResNet-18 / ResNet-50) by backpropagating target-class logits into the
final convolutional feature maps.
"""

from typing import Optional, Tuple
import io
import base64
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from loguru import logger


def _apply_jet_colormap(cam: np.ndarray) -> np.ndarray:
    """Map a normalized (H, W) float array in [0, 1] to RGB uint8 using jet palette.

    Implemented using pure numpy to avoid strict dependency on matplotlib rendering contexts.
    """
    cam = np.clip(cam, 0.0, 1.0)
    # Jet colormap piecewise linear approximation
    # 4 * x transitions: blue -> cyan -> yellow -> red
    r = np.clip(1.5 - np.abs(4.0 * cam - 3.0), 0.0, 1.0)
    g = np.clip(1.5 - np.abs(4.0 * cam - 2.0), 0.0, 1.0)
    b = np.clip(1.5 - np.abs(4.0 * cam - 1.0), 0.0, 1.0)
    rgb = np.stack([r, g, b], axis=-1) * 255.0
    return rgb.astype(np.uint8)


class GradCAM:
    """Grad-CAM generator for convolutional neural network backbones."""

    def __init__(self, model: nn.Module, target_layer: Optional[nn.Module] = None):
        """Initialize hooks on the target convolutional layer.

        Args:
            model: PyTorch classification model.
            target_layer: The target convolutional layer (defaults to model.layer4[-1] for ResNet).
        """
        self.model = model
        if target_layer is None:
            if hasattr(model, "layer4"):
                target_layer = model.layer4[-1]
            else:
                raise ValueError("Target layer must be specified if model does not expose 'layer4'")
        self.target_layer = target_layer

        self.activations: Optional[torch.Tensor] = None
        self.gradients: Optional[torch.Tensor] = None
        self._hooks = []
        self._register_hooks()

    def _register_hooks(self):
        """Attach forward and backward hooks to capture intermediate representations."""
        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()

        self._hooks.append(self.target_layer.register_forward_hook(forward_hook))
        self._hooks.append(self.target_layer.register_full_backward_hook(backward_hook))

    def remove_hooks(self):
        """Remove registered hooks to prevent memory leaks."""
        for hook in self._hooks:
            hook.remove()
        self._hooks = []

    def generate_cam(
        self,
        input_tensor: torch.Tensor,
        target_class: Optional[int] = None
    ) -> Tuple[np.ndarray, int, float]:
        """Compute the 2D Grad-CAM attention heatmap for a specific class.

        Args:
            input_tensor: Preprocessed tensor of shape (1, C, H, W).
            target_class: Target class index. If None, uses the argmax logit.

        Returns:
            Tuple of (cam_2d_normalized, target_class_idx, class_confidence_prob).
        """
        self.model.eval()
        self.model.zero_grad()

        # Grad-CAM requires gradient flow through model weights to the target layer
        with torch.enable_grad():
            tensor_copy = input_tensor.clone().detach()
            logits = self.model(tensor_copy)
            probabilities = torch.sigmoid(logits).squeeze(0)

            if target_class is None:
                target_class = int(logits.argmax(dim=-1).item())

            confidence = float(probabilities[target_class].item())

            # Backpropagate target class score
            target_score = logits[0, target_class]
            target_score.backward(retain_graph=False)

        if self.activations is None or self.gradients is None:
            logger.warning("Grad-CAM hooks failed to capture activations or gradients")
            return np.zeros((224, 224), dtype=np.float32), target_class, confidence

        # Global average pooling on gradients: alpha_k = (1 / Z) * sum(gradients)
        weights = self.gradients.mean(dim=(2, 3), keepdim=True)  # (1, C, 1, 1)

        # Weighted combination of feature maps: L_c = ReLU(sum(alpha_k * A_k))
        cam = torch.sum(weights * self.activations, dim=1, keepdim=True)  # (1, 1, H', W')
        cam = F.relu(cam)

        # Upsample to match target image dimensions (224, 224)
        target_h, target_w = input_tensor.shape[2], input_tensor.shape[3]
        cam = F.interpolate(cam, size=(target_h, target_w), mode="bilinear", align_corners=False)
        cam = cam.squeeze().cpu().numpy()

        # Min-max normalization into [0.0, 1.0]
        cam_min, cam_max = cam.min(), cam.max()
        if cam_max - cam_min > 1e-8:
            cam = (cam - cam_min) / (cam_max - cam_min)
        else:
            cam = np.zeros_like(cam)

        return cam.astype(np.float32), target_class, confidence

    def overlay_heatmap(
        self,
        original_image: Image.Image,
        cam: np.ndarray,
        alpha: float = 0.45,
    ) -> str:
        """Blend heatmap over the original image and return as base64 PNG data URI.

        Args:
            original_image: Source PIL Image.
            cam: 2D numpy array normalized in [0, 1].
            alpha: Heatmap blend opacity (0.0 = original only, 1.0 = heatmap only).

        Returns:
            Data URI string: 'data:image/png;base64,...'
        """
        # Resize original image to match heatmap dimensions
        target_size = (cam.shape[1], cam.shape[0])
        img_resized = original_image.convert("RGB").resize(target_size, Image.Resampling.LANCZOS)
        img_np = np.array(img_resized, dtype=np.float32)

        # Generate jet colormap
        heatmap_rgb = _apply_jet_colormap(cam).astype(np.float32)

        # Alpha blend
        blended = (1.0 - alpha) * img_np + alpha * heatmap_rgb
        blended = np.clip(blended, 0.0, 255.0).astype(np.uint8)

        blended_pil = Image.fromarray(blended)
        buffer = io.BytesIO()
        blended_pil.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"
