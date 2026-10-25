# TensorRT INT8 Quantization Runbook

**Status: `BLOCKED: GPU host`.**

This runbook is written and ready to execute, but it has not been run.
The development workstation is Darwin arm64 (Apple Silicon) with no
NVIDIA GPU and no CUDA runtime, so neither `trtexec` nor
`torch.cuda` is available. Nothing in this document reports measured
INT8 numbers, because none have been measured.

**Do not quote INT8 accuracy, latency, or size-reduction figures for
AegisMed in the paper, the patent, or the viva until this runbook has
been executed on an NVIDIA host and its measurement table is filled in.**

## Scope

Quantize the vision model (ResNet-18/50, 15 classes, 224×224 RGB) from
the ONNX graph produced by `scripts/deploy/export_onnx.py` into a
TensorRT INT8 engine, then verify the engine against the FP32 baseline.

INT8 affects only the vision agent. The NLP agent (BioBERT), the RAG
retriever, and the DEMAT arbitration are untouched.

## Prerequisites

- NVIDIA GPU with compute capability ≥ 8.0 (Ampere or newer)
- CUDA 12.x toolkit and cuDNN 9
- TensorRT 10.x
- `tensorrt` and `pycuda` Python packages
- A representative calibration set (see below)

## Step 1 — Produce the ONNX graph

```bash
uv pip install --python venv/bin/python -r scripts/deploy/requirements-onnx.txt
venv/bin/python scripts/deploy/export_onnx.py \
    --checkpoint models/vision_resnet50.pth \
    --output models/vision_model.onnx
```

The parity check in that script is the FP32 reference for this runbook.
Record `parity_max_abs_diff` from the generated
`models/vision_model.onnx.metadata.json`.

## Step 2 — Build the calibration set

Calibration data determines the activation ranges, so it must represent
the deployment distribution.

- Minimum **500 images**, drawn from the same acquisition pipeline as
  clinical use (modality, view position, contrast, pathology prevalence).
- Representative class balance — do not calibrate on a single class.
- For clinical deployment this set must come from real, de-identified
  data under the Phase 4.3 IRB protocol. Synthetic X-rays are acceptable
  only for an engineering smoke test, and any result obtained that way
  must be labelled as such.

Store the calibration images and their labels outside the repository
(they are not research artefacts and may carry patient data).

## Step 3 — Build the INT8 engine

```bash
trtexec --onnx=models/vision_model.onnx \
        --saveEngine=models/vision_model_int8.plan \
        --int8 \
        --calibCache=models/vision_calib.cache \
        --shapes=input:1x3x224x224
```

Generate the calibration cache first with TensorRT's
`CalibrationEntropyCalibrator2`, or reuse a cache generated for an
earlier revision of the same model.

## Step 4 — Verify before believing

Measure, do not assume. Run the engine and the FP32 baseline over the
same held-out set and record:

| Metric | FP32 baseline | INT8 engine | Acceptable? |
|---|---|---|---|
| Top-1 accuracy | _measure_ | _measure_ | ≤ 1 point drop |
| Top-3 accuracy | _measure_ | _measure_ | ≤ 1 point drop |
| Mean confidence | _measure_ | _measure_ | ≤ 0.02 drift |
| Expected calibration error | _measure_ | _measure_ | ≤ 0.02 drift |
| Mean latency (batch 1) | _measure_ | _measure_ | _record_ |
| Engine size | _measure_ | _measure_ | _record_ |

If the calibration error drifts materially, the INT8 model is not
calibrated — discard it and recalibrate before any further evaluation.

## Step 5 — Wire the engine into the vision agent

The vision agent (`src/agents/vision/agent.py`) currently loads a
PyTorch state dict through `get_shared_vision_model()`. A TensorRT
backend belongs behind the same seam:

1. Add a runtime selection setting (`VISION_RUNTIME=onnxruntime|tensorrt|pytorch`).
2. Implement the ONNX Runtime and TensorRT runners with the same
   `forward(batch) -> logits` contract.
3. Keep Grad-CAM on the PyTorch path: the explainability heatmap needs
   gradients, which a quantized inference engine does not provide. A
   deployment using INT8 must either run Grad-CAM on the FP32 model or
   drop the heatmap — this trade-off must be stated, not silently taken.
4. Add the parity test in `tests/unit/test_onnx_export.py` as a
   regression guard for whichever runtime is selected.

## Step 6 — Update the evidence

Once measured, the numbers from Step 4 replace the placeholders in this
table, and only then may they be cited in the CHIL paper, the patent
specification, or the viva defence deck.

## Fallback

If INT8 validation fails or the hardware never arrives, the shipped
deployment path is the CPU ONNX Runtime graph from
`scripts/deploy/export_onnx.py`. That path is verified against PyTorch
today and needs no GPU.
