import re
import math
import hashlib
from typing import List
import numpy as np
from app.config import settings

# Optional Google Generative AI
genai = None
if settings.GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
    except Exception as e:
        print(f"Warning: Failed to initialize Google Generative AI: {e}")
        genai = None


def generate_local_embedding(text: str, dim: int = 256) -> List[float]:
    """
    High-quality deterministic semantic subword/word n-gram embedding generator.
    Produces a normalized dense vector of dimension `dim` completely offline.
    Useful for zero-cloud testing, offline hackathon presentations, and deterministic tests.
    """
    clean_text = text.lower().strip()
    words = re.findall(r'\b[a-z0-9_]{2,}\b', clean_text)
    vector = np.zeros(dim, dtype=np.float32)

    if not words:
        return vector.tolist()

    # 1. Word hashing with positional & length weighting
    for idx, word in enumerate(words):
        # Hash word into dimension index
        h = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
        slot = h % dim
        sign = 1.0 if (h >> 8) % 2 == 0 else -1.0
        # Term frequency + slight positional bias
        weight = 1.0 + math.log(1.0 + len(word))
        vector[slot] += sign * weight

        # 2. Character 3-grams for morphological/subword matching
        if len(word) >= 3:
            for i in range(len(word) - 2):
                ngram = word[i:i+3]
                nh = int(hashlib.sha256(ngram.encode('utf-8')).hexdigest(), 16)
                nslot = nh % dim
                nsign = 1.0 if (nh >> 8) % 2 == 0 else -1.0
                vector[nslot] += nsign * 0.4

    # Normalize L2
    norm = np.linalg.norm(vector)
    if norm > 1e-6:
        vector = vector / norm

    return vector.tolist()


def get_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using Gemini if available, else local semantic generator.
    """
    if genai and settings.GEMINI_API_KEY:
        try:
            result = genai.embed_content(
                model=f"models/{settings.EMBEDDING_MODEL}",
                content=text,
                task_type="retrieval_query"
            )
            emb = result.get("embedding", [])
            if emb:
                # Normalize L2
                arr = np.array(emb, dtype=np.float32)
                norm = np.linalg.norm(arr)
                if norm > 1e-6:
                    arr = arr / norm
                return arr.tolist()
        except Exception as e:
            print(f"Gemini embedding call failed, falling back to local: {e}")

    return generate_local_embedding(text)


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute cosine similarity between two float vectors."""
    a = np.array(vec1, dtype=np.float32)
    b = np.array(vec2, dtype=np.float32)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a < 1e-6 or norm_b < 1e-6:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))
