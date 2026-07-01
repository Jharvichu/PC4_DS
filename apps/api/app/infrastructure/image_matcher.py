"""Perceptual-hash image similarity (Strategy pattern, same idiom as
CaregiverRoleStrategy / IntentHandler): swapping the underlying engine later
(e.g. an embeddings-based matcher) only requires a new IImageMatcher
implementation -- callers depend on the interface only (DIP, RNF 2.1)."""

from abc import ABC, abstractmethod

import imagehash
from PIL import Image


class IImageMatcher(ABC):
    """Extension point: compute a hash for an image and compare two hashes."""

    @abstractmethod
    def compute_hash(self, image: Image.Image) -> str:
        pass

    @abstractmethod
    def similarity(self, hash_a: str, hash_b: str) -> float:
        """Return a score in [0.0, 1.0]; 1.0 means identical."""
        pass


class PerceptualHashMatcher(IImageMatcher):
    """Uses imagehash.phash (DCT-based perceptual hash), hash_size=8 (64-bit)."""

    HASH_SIZE = 8

    def compute_hash(self, image: Image.Image) -> str:
        return str(imagehash.phash(image, hash_size=self.HASH_SIZE))

    def similarity(self, hash_a: str, hash_b: str) -> float:
        ha = imagehash.hex_to_hash(hash_a)
        hb = imagehash.hex_to_hash(hash_b)
        max_bits = self.HASH_SIZE * self.HASH_SIZE
        distance = ha - hb  # Hamming distance
        return max(0.0, 1.0 - (distance / max_bits))
