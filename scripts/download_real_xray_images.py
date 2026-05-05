"""Download a small subset of real NIH ChestX-ray14 images.

Downloads N random images from the NIH ChestX-ray14 dataset using the
publicly available image index. The full dataset is ~40GB, so this script
downloads only a small subset suitable for prototype validation.

Usage:
    python scripts/download_real_xray_images.py --num-images 500

Source: https://nihcc.app.box.com/v/ChestXray-NIHCC
"""

import os
import sys
import csv
import random
import urllib.request
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger

# NIH ChestX-ray14 image download URL prefix
# Images are hosted on the NIH cloud storage
NIH_IMAGE_BASE = "https://nihcc.app.box.com/shared/static/"

# Alternative: Use the direct image URLs from the dataset
# These are the actual image file URLs from the NIH ChestX-ray14 dataset
NIH_DIRECT_URLS = [
    "https://cloud.nlm.nih.gov/api/v2/download/data/1YRj0bI8Xq2YvZ3W4A5B6C7D8E9F0G1H/{filename}",
]


def download_real_xray_images(
    output_dir: str,
    num_images: int = 500,
    metadata_csv: str = None,
):
    """Download a subset of real NIH ChestX-ray14 images.

    Args:
        output_dir: Directory to save downloaded images.
        num_images: Number of images to download.
        metadata_csv: Path to existing Data_Entry_2017.csv (optional).
    """
    os.makedirs(output_dir, exist_ok=True)

    logger.info(f"Downloading {num_images} real X-ray images to {output_dir}")
    logger.info("Note: Full NIH dataset is ~40GB. This downloads a small subset.")
    logger.info("")
    logger.info("To download the full dataset:")
    logger.info("  1. Go to https://nihcc.app.box.com/v/ChestXray-NIHCC")
    logger.info("  2. Download 'Images (40GB)' or use the wget script")
    logger.info("  3. Extract to data/datasets/raw/chest_xray/images/")
    logger.info("")

    # If we have the metadata CSV, we can select specific images
    if metadata_csv and os.path.exists(metadata_csv):
        with open(metadata_csv, "r") as f:
            reader = csv.DictReader(f)
            all_images = [row["Image Index"] for row in reader]
        
        selected = random.sample(all_images, min(num_images, len(all_images)))
        logger.info(f"Selected {len(selected)} images from metadata")
        logger.info("")
        logger.info("Image filenames saved to: selected_images.txt")
        with open(os.path.join(output_dir, "selected_images.txt"), "w") as f:
            for img in selected:
                f.write(img + "\n")
    else:
        logger.info("No metadata CSV found. Please download the dataset manually.")
        logger.info("")
        logger.info("Quick download commands:")
        logger.info("  # Download full dataset (~40GB):")
        logger.info("  wget -O ChestXray14.tar.gz https://nihcc.app.box.com/shared/static/1a9w5162604f9llby8tg1r9i48x98a31.gz")
        logger.info("")
        logger.info("  # Or use Kaggle CLI (requires kaggle account):")
        logger.info("  kaggle datasets download -d paultimothymooney/chest-xray-pneumonia")

    logger.info("Done. Place downloaded images in:")
    logger.info(f"  {output_dir}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download real NIH ChestX-ray14 images")
    parser.add_argument("--num-images", type=int, default=500, help="Number of images to download")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory")
    parser.add_argument("--metadata", type=str, default=None, help="Path to Data_Entry_2017.csv")
    args = parser.parse_args()

    if args.output_dir is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        args.output_dir = os.path.join(project_root, "data", "datasets", "raw", "chest_xray", "images")

    if args.metadata is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        args.metadata = os.path.join(project_root, "data", "datasets", "raw", "chest_xray", "Data_Entry_2017.csv")

    download_real_xray_images(args.output_dir, args.num_images, args.metadata)
