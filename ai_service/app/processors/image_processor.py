import io
import base64
from typing import Optional, Tuple
import numpy as np
from PIL import Image, ImageOps
import cv2
from app.utils.logging import get_logger

logger = get_logger(__name__)

MAX_DIMENSION = 1920
JPEG_QUALITY = 85


class ImageProcessor:
    """Handles image loading, validation, and preprocessing for AI models."""

    def load_from_bytes(self, data: bytes) -> np.ndarray:
        try:
            pil_image = Image.open(io.BytesIO(data))
            pil_image = ImageOps.exif_transpose(pil_image)
            if pil_image.mode not in ("RGB", "L"):
                pil_image = pil_image.convert("RGB")
            return np.array(pil_image)
        except Exception as e:
            logger.error("image_load_failed", error=str(e))
            raise ValueError(f"Cannot load image: {e}")

    def resize_for_inference(self, image: np.ndarray, max_dim: int = MAX_DIMENSION) -> np.ndarray:
        h, w = image.shape[:2]
        if max(h, w) <= max_dim:
            return image
        scale = max_dim / max(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    def normalize(self, image: np.ndarray) -> np.ndarray:
        """Normalize to [0, 1] float32."""
        return image.astype(np.float32) / 255.0

    def to_tensor(self, image: np.ndarray):
        """Convert HWC numpy array to CHW torch tensor."""
        import torch
        tensor = torch.from_numpy(image).permute(2, 0, 1).unsqueeze(0)
        return tensor

    def preprocess(self, data: bytes) -> Tuple[np.ndarray, np.ndarray]:
        """Full pipeline: load → resize → return (original, preprocessed)."""
        original = self.load_from_bytes(data)
        resized = self.resize_for_inference(original)
        return original, resized

    def encode_thumbnail(self, image: np.ndarray, max_size: int = 256) -> str:
        """Return base64-encoded JPEG thumbnail."""
        h, w = image.shape[:2]
        scale = min(max_size / h, max_size / w, 1.0)
        if scale < 1.0:
            image = cv2.resize(image, (int(w * scale), int(h * scale)))
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if image.shape[2] == 3 else image
        pil = Image.fromarray(rgb)
        buf = io.BytesIO()
        pil.save(buf, format="JPEG", quality=70)
        return base64.b64encode(buf.getvalue()).decode()


image_processor = ImageProcessor()
