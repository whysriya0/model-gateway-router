
import numpy as np
from sentence_transformers import SentenceTransformer


class SemanticCache:

    def __init__(self, threshold=0.92):
        self.threshold = threshold
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")

        # Store cached prompts and answers
        self.cache = []

    def get(self, prompt, context="default"):

        # Step 1: Exact-match lookup
        for entry in self.cache:
            if entry["prompt"] == prompt and entry["context"] == context:
                return entry["answer"], "exact"

        # Step 2: Convert prompt to embedding
        embedding = self.encoder.encode(
            prompt,
            normalize_embeddings=True
        )

        best_similarity = -1
        best_answer = None

        # Step 3: Compare with cached embeddings
        for entry in self.cache:

            if entry["context"] != context:
                continue

            similarity = float(
                np.dot(embedding, entry["embedding"])
            )

            if similarity > best_similarity:
                best_similarity = similarity
                best_answer = entry["answer"]

        # Step 4: Check similarity threshold
        if best_similarity >= self.threshold:
            return best_answer, "semantic"

        return None, "miss"

    def put(self, prompt, answer, context="default"):

        embedding = self.encoder.encode(
            prompt,
            normalize_embeddings=True
        )

        self.cache.append({
            "prompt": prompt,
            "answer": answer,
            "embedding": embedding,
            "context": context
        })

    def size(self):
        return len(self.cache)
