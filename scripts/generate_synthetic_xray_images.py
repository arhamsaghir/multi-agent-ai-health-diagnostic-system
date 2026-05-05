"""Generate synthetic chest X-ray images using vectorized numpy operations.

Creates realistic-looking chest X-ray images with disease-like patterns
using efficient numpy array operations instead of per-pixel PIL loops.
"""

import os
import sys
import json
import csv
import random
import numpy as np
from pathlib import Path
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger

DISEASE_LABELS = [
    "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration",
    "Mass", "Nodule", "Pneumonia", "Pneumothorax",
    "Consolidation", "Edema", "Emphysema", "Fibrosis",
    "Pleural_Thickening", "Hernia", "No Finding",
]


def generate_chest_xray(width=512, height=512, diseases=None, seed=None):
    """Generate a synthetic chest X-ray image using numpy operations."""
    if seed is not None:
        np.random.seed(seed)
    if diseases is None:
        diseases = []

    # Create coordinate grids
    y, x = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')
    cx, cy = width // 2, height // 2 + 50

    # Base image with noise
    img = np.random.normal(40, 8, (height, width)).astype(np.float32)

    # Lung parameters
    rib_w = int(width * 0.7)
    lung_h = int(height * 0.65 * 0.85)
    lung_w = int(rib_w * 0.32)
    left_lx = cx - int(rib_w * 0.28)
    right_lx = cx + int(rib_w * 0.28)
    lung_y = cy - 30

    # Draw lungs
    for lx in [left_lx, right_lx]:
        dx = (x - lx) / lung_w
        dy = (y - lung_y) / lung_h
        mask = (dx*dx + dy*dy) < 1
        lung_vals = 140 + 30 * (1 - dx[mask]**2 - dy[mask]**2) + np.random.normal(0, 5, np.sum(mask))
        img[mask] = lung_vals

    # Draw spine
    spine_mask = (x > cx - 20) & (x < cx + 10) & (y > cy - int(lung_h * 0.9)) & (y < cy + int(lung_h * 0.8))
    vertebra_pattern = ((y - (cy - int(lung_h * 0.9))) % 25) < 15
    img[spine_mask & vertebra_pattern] = 60
    img[spine_mask & ~vertebra_pattern] = 100

    # Draw heart
    hx, hy = cx - 20, cy + 40
    hw, hh = int(rib_w * 0.22), int(lung_h * 0.4)
    dx = (x - hx) / hw
    dy = (y - hy) / hh
    heart_mask = (dx*dx + dy*dy) < 1
    img[heart_mask] = np.maximum(img[heart_mask], 100 + 40 * (1 - dx[heart_mask]**2 - dy[heart_mask]**2))

    # Draw clavicles
    for side in [-1, 1]:
        clx = cx + side * int(rib_w * 0.25)
        cly = cy - int(lung_h * 0.85)
        for t in range(-60, 60):
            px = int(clx + t * side)
            py = int(cly + abs(t) * 0.3)
            img[max(0, py-2):min(height, py+2), max(0, px-3):min(width, px+3)] = 80

    # Draw diaphragm
    for side in [-1, 1]:
        dx2 = cx + side * int(rib_w * 0.25)
        dy2 = cy + int(lung_h * 0.8)
        for t in range(-100, 100):
            px = int(dx2 + t)
            py = int(dy2 - abs(t) * 0.15 + (t/100)**2 * 25)
            img[max(0, py-2):min(height, py+2), max(0, px-2):min(width, px+2)] = 90

    # Apply disease patterns
    for disease in diseases:
        img = apply_disease(img, disease, width, height, cx, cy, rib_w, lung_w, lung_h, left_lx, right_lx, lung_y)

    # Normalize and convert
    img = np.clip((img - 60) * 1.3 + 40, 0, 255).astype(np.uint8)
    return img


def apply_disease(img, disease, w, h, cx, cy, rib_w, lung_w, lung_h, left_lx, right_lx, lung_y):
    """Apply disease pattern using numpy operations."""
    y, x = np.meshgrid(np.arange(h), np.arange(w), indexing='ij')

    def ellipse_mask(center_x, center_y, rw, rh):
        dx = (x - center_x) / rw
        dy = (y - center_y) / rh
        return (dx*dx + dy*dy) < 1, dx, dy

    if disease == "Cardiomegaly":
        mask, dx, dy = ellipse_mask(cx - 20, cy + 40, int(rib_w * 0.35), int(lung_h * 0.5))
        img[mask] = np.maximum(img[mask], 130 + 30 * (1 - dx[mask]**2 - dy[mask]**2))

    elif disease == "Pneumothorax":
        mask, dx, dy = ellipse_mask(right_lx + int(lung_w * 0.5), lung_y - int(lung_h * 0.3), 50, 60)
        img[mask] = np.minimum(img[mask], 20)

    elif disease == "Effusion":
        for side in [-1, 1]:
            mask, dx, dy = ellipse_mask(cx + side * int(rib_w * 0.3), lung_y + int(lung_h * 0.7), 60, 40)
            fluid_mask = mask & (dy > 0)
            img[fluid_mask] = 180

    elif disease == "Infiltration":
        rng = np.random.default_rng(int(hash(f"inf_{cy}") % (2**31)))
        for _ in range(12):
            ix = rng.choice([left_lx, right_lx]) + rng.integers(-lung_w, lung_w)
            iy = lung_y + rng.integers(-int(lung_h * 0.5), int(lung_h * 0.5))
            ir = rng.integers(15, 40)
            mask, dx, dy = ellipse_mask(ix, iy, ir, ir)
            img[mask] = np.maximum(img[mask], 150 + 40 * (1 - dx[mask]**2 - dy[mask]**2))

    elif disease == "Mass":
        mx = random.choice([left_lx, right_lx])
        mr = random.randint(30, 60)
        mask, dx, dy = ellipse_mask(mx, lung_y, mr, mr)
        img[mask] = np.maximum(img[mask], 160 + 50 * (1 - dx[mask]**2 - dy[mask]**2))

    elif disease == "Nodule":
        nx = random.choice([left_lx, right_lx]) + random.randint(-30, 30)
        ny = lung_y + random.randint(-30, 30)
        nr = random.randint(8, 15)
        mask, dx, dy = ellipse_mask(nx, ny, nr, nr)
        img[mask] = np.maximum(img[mask], 170 + 40 * (1 - dx[mask]**2 - dy[mask]**2))

    elif disease == "Pneumonia":
        px = random.choice([left_lx, right_lx])
        mask, dx, dy = ellipse_mask(px, lung_y + int(lung_h * 0.2), int(lung_w * 0.6), int(lung_h * 0.5))
        img[mask] = np.maximum(img[mask], 160 + 40 * (1 - dx[mask]**2 - dy[mask]**2))

    elif disease == "Atelectasis":
        ax = random.choice([left_lx, right_lx])
        mask, dx, dy = ellipse_mask(ax, lung_y, int(lung_w * 0.4), int(lung_h * 0.6))
        img[mask] = np.maximum(img[mask], 140 + 50 * (1 - dx[mask]**2 - dy[mask]**2))

    elif disease == "Consolidation":
        cx2 = random.choice([left_lx, right_lx])
        cy2 = lung_y + random.randint(-20, 20)
        cr = random.randint(40, 70)
        mask, dx, dy = ellipse_mask(cx2, cy2, cr, cr)
        img[mask] = np.maximum(img[mask], 155 + 45 * (1 - dx[mask]**2 - dy[mask]**2))

    elif disease == "Edema":
        mask, dx, dy = ellipse_mask(cx, lung_y, 80, 60)
        img[mask] = np.maximum(img[mask], 150 + 40 * (1 - dx[mask]**2 - dy[mask]**2))

    elif disease == "Emphysema":
        for lx in [left_lx, right_lx]:
            mask, dx, dy = ellipse_mask(lx, lung_y, lung_w, lung_h)
            img[mask] = (img[mask] * 0.85).astype(np.uint8)

    elif disease == "Fibrosis":
        rng = np.random.default_rng(int(hash(f"fib_{cy}") % (2**31)))
        for _ in range(25):
            x1 = rng.choice([left_lx, right_lx]) + rng.integers(-lung_w, lung_w)
            y1 = lung_y + rng.integers(-lung_h, lung_h)
            x2 = x1 + rng.integers(-40, 40)
            y2 = y1 + rng.integers(-40, 40)
            # Draw line using Bresenham-like approach
            n_pts = max(abs(x2-x1), abs(y2-y1))
            if n_pts > 0:
                pts_x = np.linspace(x1, x2, n_pts).astype(int)
                pts_y = np.linspace(y1, y2, n_pts).astype(int)
                valid = (pts_x >= 0) & (pts_x < w) & (pts_y >= 0) & (pts_y < h)
                img[pts_y[valid], pts_x[valid]] = 160

    elif disease == "Pleural_Thickening":
        for side in [-1, 1]:
            px = cx + side * int(rib_w * 0.45)
            mask = (x > px - 15) & (x < px + 15) & (y > lung_y - lung_h) & (y < lung_y + lung_h)
            img[mask] = 140

    elif disease == "Hernia":
        hx = cx + random.choice([-1, 1]) * 30
        hy = lung_y + int(lung_h * 0.8)
        mask, dx, dy = ellipse_mask(hx, hy, 40, 40)
        img[mask] = np.maximum(img[mask], 140 + 40 * (1 - dx[mask]**2 - dy[mask]**2))

    return img


def generate_dataset(output_dir: str, images_per_class: int = 300):
    """Generate synthetic chest X-ray dataset."""
    os.makedirs(output_dir, exist_ok=True)
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    logger.info(f"Generating {images_per_class * len(DISEASE_LABELS)} synthetic chest X-ray images")
    logger.info(f"Target: {images_per_class} images per disease class")

    metadata = []
    total_start = time.time()

    for idx, disease in enumerate(DISEASE_LABELS):
        disease_start = time.time()
        diseases_list = [] if disease == "No Finding" else [disease]
        label_str = disease if disease == "No Finding" else disease

        for i in range(images_per_class):
            seed = (idx * 10000 + i) * 7 + 42  # Deterministic seed
            img_array = generate_chest_xray(diseases=diseases_list, seed=seed)

            filename = f"syn_{disease.lower().replace(' ', '_')}_{i:04d}.png"
            filepath = os.path.join(images_dir, filename)

            # Save using numpy directly (faster than PIL)
            from PIL import Image
            Image.fromarray(img_array, mode='L').save(filepath)

            metadata.append({
                "Image Index": filename,
                "Finding Labels": label_str,
                "Follow-up #": 0,
                "Patient ID": f"PID_{10000 + idx * 1000 + i}",
                "Patient Age": 30 + (i % 60),
                "Patient Sex": "M" if i % 2 == 0 else "F",
                "View Position": "PA" if i % 3 != 0 else "AP",
                "Original Image Width": 512,
                "Original Image Height": 512,
                "OriginalImagePixelSpacing_x": 0.143,
                "OriginalImagePixelSpacing_y": 0.143,
            })

        elapsed = time.time() - disease_start
        logger.info(f"  {disease}: {images_per_class} images in {elapsed:.1f}s")

    # Save metadata CSV
    csv_path = os.path.join(output_dir, "Data_Entry_2017.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Image Index", "Finding Labels", "Follow-up #",
            "Patient ID", "Patient Age", "Patient Sex",
            "View Position", "Original Image Width",
            "Original Image Height", "OriginalImagePixelSpacing_x",
            "OriginalImagePixelSpacing_y",
        ])
        writer.writeheader()
        for row in metadata:
            writer.writerow(row)

    # Save class distribution
    dist = {}
    for row in metadata:
        dist[row["Finding Labels"]] = dist.get(row["Finding Labels"], 0) + 1

    dist_path = os.path.join(output_dir, "class_distribution.json")
    with open(dist_path, "w") as f:
        json.dump(dist, f, indent=2)

    total_elapsed = time.time() - total_start
    logger.info(f"Generated {len(metadata)} images → {images_dir}")
    logger.info(f"Total time: {total_elapsed:.1f}s")
    logger.info(f"Class distribution:")
    for label, count in sorted(dist.items(), key=lambda x: -x[1]):
        logger.info(f"  {label}: {count}")


if __name__ == "__main__":
    output_base = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "datasets", "raw", "chest_xray",
    )
    generate_dataset(output_base, images_per_class=300)
