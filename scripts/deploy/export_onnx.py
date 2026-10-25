"""Export the AegisMed vision model to ONNX for CPU on-prem inference.

The container deployment runs the PyTorch model directly. This script
produces an ONNX graph of the same network so an inference runtime
(ONNX Runtime now, TensorRT INT8 on a GPU host later) can serve the same
predictions without the PyTorch dependency.

The export is verified against PyTorch before the artifact is accepted:
the script compares both runtimes on the same input and refuses to write
a model whose outputs drift beyond the configured tolerance.

Usage:
    python scripts/deploy/export_onnx.py \
        --checkpoint models/vision_resnet50.pth \
        --output models/vision_resnet50.onnx

TensorRT INT8 quantization is BLOCKED on this workstation (no NVIDIA
GPU). See docs/deploy/TENSORRT_INT8_RUNBOOK.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import torch
import torch.nn as nn
from torchvision import models

from config import settings


def detect_architecture(state_dict: dict[str, Any]) -> str:
    """Infer the ResNet variant from the classifier input dimension.

    Mirrors src/agents/vision/agent.py: fc input dim 512 is ResNet-18,
    2048 is ResNet-50.
    """
    fc_weight = state_dict.get("fc.weight")
    if fc_weight is None:
        raise ValueError("Checkpoint has no 'fc.weight' entry — not a ResNet classifier")
    fc_in_features = int(fc_weight.shape[1])
    return "resnet18" if fc_in_features == 512 else "resnet50"


def build_model(arch: str, num_classes: int) -> nn.Module:
    """Instantiate the vision architecture with the project's class count."""
    builder = {"resnet18": models.resnet18, "resnet50": models.resnet50}.get(arch)
    if builder is None:
        raise ValueError(f"Unsupported architecture: {arch}")
    model = builder(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


def load_checkpoint(checkpoint_path: Path) -> tuple[nn.Module, str, bool]:
    """Build the model and load weights if the checkpoint exists.

    Returns the model, the detected architecture, and whether trained
    weights were actually applied.
    """
    if not checkpoint_path.exists():
        arch = settings.vision_model_name
        print(f"[export] No checkpoint at {checkpoint_path} — exporting untrained weights")
        return build_model(arch, settings.num_disease_classes), arch, False

    state_dict = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    arch = detect_architecture(state_dict)
    model = build_model(arch, settings.num_disease_classes)
    model.load_state_dict(state_dict)
    print(f"[export] Loaded {arch} checkpoint from {checkpoint_path}")
    return model, arch, True


def export_onnx(
    model: nn.Module,
    output_path: Path,
    opset: int,
    batch_size: int,
    image_size: int,
) -> None:
    """Write the ONNX graph to disk."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dummy = torch.randn(batch_size, 3, image_size, image_size)

    torch.onnx.export(
        model,
        (dummy,),
        str(output_path),
        input_names=["input"],
        output_names=["logits"],
        dynamic_axes={"input": {0: "batch"}, "logits": {0: "batch"}},
        opset_version=opset,
        do_constant_folding=True,
        # The TorchScript exporter is used deliberately: the torch.export
        # (dynamo) path needs an onnxscript build matching the installed
        # torch version, which is not pinned in this environment.
        dynamo=False,
    )
    print(f"[export] Wrote ONNX graph to {output_path}")


def verify_parity(
    model: nn.Module,
    onnx_path: Path,
    tolerance: float,
    batch_size: int,
    image_size: int,
) -> tuple[float, np.ndarray, np.ndarray]:
    """Compare PyTorch and ONNX Runtime outputs on the same random input."""
    import onnxruntime as ort

    session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name

    torch_model = model.eval()
    sample = torch.randn(batch_size, 3, image_size, image_size)

    with torch.no_grad():
        torch_logits = torch_model(sample).numpy()

    onnx_logits = session.run(None, {input_name: sample.numpy()})[0]

    max_abs_diff = float(np.max(np.abs(torch_logits - onnx_logits)))
    print(f"[verify] max |torch - onnxruntime| = {max_abs_diff:.3e} (tolerance {tolerance:.1e})")
    if max_abs_diff > tolerance:
        raise SystemExit(
            f"[verify] FAILED — parity drift {max_abs_diff:.3e} exceeds tolerance {tolerance:.1e}"
        )
    print("[verify] Parity OK")
    return max_abs_diff, torch_logits, onnx_logits


def sha256(path: Path) -> str:
    """Checksum of the exported artifact for supply-chain auditing."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_metadata(output_path: Path, metadata: dict[str, Any]) -> Path:
    """Write the audit sidecar next to the exported graph."""
    metadata_path = output_path.with_suffix(output_path.suffix + ".metadata.json")
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--checkpoint",
        default=settings.vision_model_path,
        help="Path to the trained vision checkpoint (.pth)",
    )
    parser.add_argument(
        "--output",
        default="models/vision_model.onnx",
        help="Destination path for the ONNX graph",
    )
    parser.add_argument("--opset", type=int, default=17, help="ONNX opset version")
    parser.add_argument("--batch-size", type=int, default=1, help="Batch size used for export")
    parser.add_argument("--image-size", type=int, default=224, help="Input image edge length")
    parser.add_argument(
        "--tolerance",
        type=float,
        default=1e-4,
        help="Maximum accepted absolute logit difference between runtimes",
    )
    parser.add_argument("--no-verify", action="store_true", help="Skip the parity check")
    args = parser.parse_args()

    checkpoint_path = Path(args.checkpoint)
    output_path = Path(args.output)

    model, arch, trained = load_checkpoint(checkpoint_path)
    model.eval()

    export_onnx(
        model,
        output_path,
        opset=args.opset,
        batch_size=args.batch_size,
        image_size=args.image_size,
    )

    max_abs_diff = None
    if not args.no_verify:
        max_abs_diff, _, _ = verify_parity(
            model,
            output_path,
            tolerance=args.tolerance,
            batch_size=args.batch_size,
            image_size=args.image_size,
        )

    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "architecture": arch,
        "trained_weights": trained,
        "source_checkpoint": str(checkpoint_path),
        "opset": args.opset,
        "input_shape": [args.batch_size, 3, args.image_size, args.image_size],
        "output_shape": [args.batch_size, settings.num_disease_classes],
        "num_disease_classes": settings.num_disease_classes,
        "parity_max_abs_diff": max_abs_diff,
        "parity_tolerance": args.tolerance,
        "sha256": sha256(output_path),
        "size_bytes": output_path.stat().st_size,
        "torch_version": torch.__version__,
    }

    metadata_path = write_metadata(output_path, metadata)
    print(f"[export] Wrote metadata to {metadata_path}")

    if not trained:
        print(
            "[export] WARNING — artifact contains untrained weights; "
            "re-run with a trained checkpoint before clinical use"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
