"""Tests for the ONNX export scaffold (scripts/deploy/export_onnx.py).

The export is only useful if the ONNX graph produces the same logits as
PyTorch, so parity is a first-class assertion rather than an optional
step.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import torch
import torch.nn as nn

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPORT_SCRIPT = PROJECT_ROOT / "scripts" / "deploy" / "export_onnx.py"


def _load_export_module():
    """Import the deploy script, which is not part of an installed package."""
    spec = importlib.util.spec_from_file_location("export_onnx", EXPORT_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def export_module():
    return _load_export_module()


class TestArchitectureDetection:
    """The exported graph must match the checkpoint's architecture."""

    def test_detects_resnet18_from_fc_input_dim(self, export_module) -> None:
        state_dict = {"fc.weight": torch.zeros(15, 512)}
        assert export_module.detect_architecture(state_dict) == "resnet18"

    def test_detects_resnet50_from_fc_input_dim(self, export_module) -> None:
        state_dict = {"fc.weight": torch.zeros(15, 2048)}
        assert export_module.detect_architecture(state_dict) == "resnet50"

    def test_rejects_checkpoint_without_classifier(self, export_module) -> None:
        with pytest.raises(ValueError, match="fc.weight"):
            export_module.detect_architecture({"conv1.weight": torch.zeros(1)})

    def test_built_model_has_project_class_count(self, export_module) -> None:
        model = export_module.build_model("resnet18", 15)
        output = model(torch.zeros(1, 3, 224, 224))
        assert output.shape == (1, 15)


def _tiny_image_model() -> nn.Module:
    """A small conv net matching the (batch, 3, H, W) input contract."""
    return nn.Sequential(
        nn.Conv2d(3, 4, 3),
        nn.ReLU(),
        nn.Flatten(),
        nn.Linear(4 * 6 * 6, 2),
    ).eval()


class TestParityCheck:
    """Parity verification must accept matching runtimes and reject drift."""

    def test_accepts_matching_model(self, export_module, tmp_path: Path) -> None:
        model = _tiny_image_model()
        onnx_path = tmp_path / "tiny.onnx"
        export_module.export_onnx(
            model, onnx_path, opset=17, batch_size=1, image_size=8
        )
        max_abs_diff, torch_logits, onnx_logits = export_module.verify_parity(
            model, onnx_path, tolerance=1e-4, batch_size=1, image_size=8
        )
        assert max_abs_diff <= 1e-4
        assert torch_logits.shape == onnx_logits.shape

    def test_rejects_output_drift(self, export_module, tmp_path: Path, monkeypatch) -> None:
        model = _tiny_image_model()
        onnx_path = tmp_path / "tiny.onnx"
        export_module.export_onnx(
            model, onnx_path, opset=17, batch_size=1, image_size=8
        )

        import onnxruntime as ort

        class DriftedSession:
            def __init__(self, *args, **kwargs) -> None:
                pass

            def get_inputs(self):
                return [type("Input", (), {"name": "input"})()]

            def run(self, _outputs, _feed):
                return [torch.ones(1, 2).numpy() * 99.0]

        monkeypatch.setattr(ort, "InferenceSession", DriftedSession)
        with pytest.raises(SystemExit, match="parity drift"):
            export_module.verify_parity(
                model, onnx_path, tolerance=1e-4, batch_size=1, image_size=8
            )


@pytest.mark.skipif(
    not (PROJECT_ROOT / "models" / "vision_resnet50.pth").exists(),
    reason="vision checkpoint not available in this environment",
)
class TestRealCheckpointExport:
    """End-to-end export against the project's trained vision checkpoint."""

    def test_export_matches_pytorch(self, export_module, tmp_path: Path) -> None:
        output_path = tmp_path / "vision.onnx"
        model, arch, trained = export_module.load_checkpoint(
            PROJECT_ROOT / "models" / "vision_resnet50.pth"
        )
        assert trained is True
        assert arch in {"resnet18", "resnet50"}

        export_module.export_onnx(model, output_path, opset=17, batch_size=1, image_size=224)
        max_abs_diff, _, _ = export_module.verify_parity(
            model, output_path, tolerance=1e-4, batch_size=1, image_size=224
        )
        assert max_abs_diff <= 1e-4

    def test_metadata_records_audit_trail(self, export_module, tmp_path: Path) -> None:
        output_path = tmp_path / "vision.onnx"
        model, arch, trained = export_module.load_checkpoint(
            PROJECT_ROOT / "models" / "vision_resnet50.pth"
        )
        export_module.export_onnx(model, output_path, opset=17, batch_size=1, image_size=224)

        metadata_path = export_module.write_metadata(
            output_path,
            {
                "architecture": arch,
                "trained_weights": trained,
                "opset": 17,
                "input_shape": [1, 3, 224, 224],
                "num_disease_classes": 15,
                "sha256": export_module.sha256(output_path),
            },
        )
        assert metadata_path.exists()
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert metadata["trained_weights"] is True
        assert metadata["opset"] == 17
        assert metadata["input_shape"] == [1, 3, 224, 224]
        assert metadata["num_disease_classes"] == 15
        assert len(metadata["sha256"]) == 64
