"""Image preprocessing for medical imaging (X-ray, MRI, scans)."""

from typing import Optional, Union
import numpy as np
from PIL import Image, ImageEnhance


class ImagePreprocessor:
    """Preprocesses medical images for model input and augmentation."""

    DEFAULT_SIZE = (224, 224)
    IMAGENET_MEAN = [0.485, 0.456, 0.406]
    IMAGENET_STD = [0.229, 0.224, 0.225]

    def __init__(self, target_size: tuple[int, int] = DEFAULT_SIZE):
        self.target_size = target_size

    def load(self, path: str) -> Image.Image:
        """Load image from file path."""
        img = Image.open(path)
        if img.mode != "RGB":
            img = img.convert("RGB")
        return img

    def resize(self, img: Image.Image) -> Image.Image:
        """Resize image to target size with aspect ratio preservation."""
        return img.resize(self.target_size, Image.Resampling.LANCZOS)

    def normalize(self, img: Image.Image) -> np.ndarray:
        """Normalize pixel values using ImageNet statistics."""
        arr = np.array(img, dtype=np.float32) / 255.0
        for i in range(3):
            arr[:, :, i] = (arr[:, :, i] - self.IMAGENET_MEAN[i]) / self.IMAGENET_STD[i]
        return arr

    def enhance_contrast(self, img: Image.Image, factor: float = 1.5) -> Image.Image:
        """Enhance image contrast — useful for X-ray images."""
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(factor)

    def enhance_brightness(self, img: Image.Image, factor: float = 1.2) -> Image.Image:
        """Enhance image brightness."""
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(factor)

    def apply_histogram_equalization(self, img: Image.Image) -> Image.Image:
        """Apply contrast-limited adaptive histogram equalization."""
        arr = np.array(img)
        result = np.zeros_like(arr)
        for i in range(3):
            img_gray = arr[:, :, i]
            hist, bins = np.histogram(img_gray.flatten(), 256, [0, 256])
            cdf = hist.cumsum()
            cdf_normalized = (cdf - cdf.min()) * 255 / (cdf.max() - cdf.min())
            cdf_m = np.ma.filled(cdf_normalized, 0).astype("uint8")
            result[:, :, i] = cdf_m[img_gray]
        return Image.fromarray(result)

    def augment_flip_horizontal(self, img: Image.Image) -> Image.Image:
        """Horizontal flip augmentation."""
        return img.transpose(Image.FLIP_LEFT_RIGHT)

    def augment_rotation(self, img: Image.Image, degrees: int = 15) -> Image.Image:
        """Random rotation augmentation."""
        import random
        angle = random.uniform(-degrees, degrees)
        return img.rotate(angle, resample=Image.BILINEAR, fillcolor=0)

    def preprocess_for_model(self, img: Union[str, Image.Image]) -> np.ndarray:
        """Full preprocessing pipeline for model inference.

        Args:
            img: File path string or PIL Image.

        Returns:
            Numpy array (H, W, C) normalized and ready for model input.
        """
        if isinstance(img, str):
            img = self.load(img)

        img = self.resize(img)
        arr = self.normalize(img)

        # Transpose to (C, H, W) format for PyTorch
        arr = arr.transpose(2, 0, 1)
        return arr

    def preprocess_batch(self, paths: list[str]) -> np.ndarray:
        """Preprocess a batch of images for training.

        Args:
            paths: List of image file paths.

        Returns:
            Numpy array (N, C, H, W) for batch model input.
        """
        batch = [self.preprocess_for_model(p) for p in paths]
        return np.array(batch)

    def generate_augmented(self, img: Image.Image, n_augmentations: int = 4) -> list[Image.Image]:
        """Generate augmented versions of an image for training.

        Args:
            img: PIL Image to augment.
            n_augmentations: Number of augmented images to generate.

        Returns:
            List of augmented PIL Images.
        """
        augmented = []
        augmentations = [
            self.augment_flip_horizontal,
            lambda x: self.augment_rotation(x, 10),
            lambda x: self.augment_rotation(x, 20),
            lambda x: self.enhance_contrast(x, 1.3),
            lambda x: self.enhance_brightness(x, 1.1),
            lambda x: self.apply_histogram_equalization(x),
        ]

        import random
        selected = random.sample(augmentations, min(n_augmentations, len(augmentations)))
        for aug_func in selected:
            augmented.append(augment_func(img))

        return augmented
