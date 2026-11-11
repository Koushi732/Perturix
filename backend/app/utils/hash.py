import hashlib


def calculate_sha256(content: bytes) -> str:
    """Calculates the SHA-256 hash of the given bytes."""
    return hashlib.sha256(content).hexdigest()
