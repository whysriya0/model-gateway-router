
import json
from pathlib import Path

import joblib
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parent.parent

PROMPTS = ROOT / "evals" / "prompts.json"
SCORES = ROOT / "evals" / "scores.jsonl"
MODEL_FILE = ROOT / "learned_router.joblib"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Load the local embedding model
encoder = SentenceTransformer(EMBEDDING_MODEL)


def load_training_data():
    prompts = json.loads(
        PROMPTS.read_text(encoding="utf-8")
    )

    scores = [
        json.loads(line)
        for line in SCORES.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

    # Map prompt ID and strategy to its score
    score_map = {
        (s["id"], s["strategy"]): s["score"]
        for s in scores
    }

    texts = []
    labels = []

    for p in prompts:

        # Never train on development or test prompts
        if p["split"] != "train":
            continue

        key = (p["id"], "small")

        if key not in score_map:
            continue

        small_score = score_map[key]

        # 1 means the small model is sufficient
        label = int(small_score >= 0.8)

        texts.append(p["prompt"])
        labels.append(label)

    return texts, labels


def train_router():
    texts, labels = load_training_data()

    if len(set(labels)) < 2:
        raise ValueError(
            "Training requires both successful "
            "and unsuccessful small-model examples."
        )

    # Convert prompts to embedding vectors
    X = encoder.encode(
        texts,
        normalize_embeddings=True
    )

    # Train a binary classifier
    classifier = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42
    )

    classifier.fit(X, labels)

    # Save the trained classifier
    joblib.dump(classifier, MODEL_FILE)

    print("Training completed")
    print("Training examples:", len(texts))
    print("Positive labels:", sum(labels))
    print("Negative labels:", len(labels) - sum(labels))


def predict_route(prompt, threshold=0.8):
    classifier = joblib.load(MODEL_FILE)

    # Convert the new prompt into an embedding
    embedding = encoder.encode(
        [prompt],
        normalize_embeddings=True
    )

    probabilities = classifier.predict_proba(embedding)[0]

    # Find the probability of class 1
    positive_index = list(classifier.classes_).index(1)
    probability = probabilities[positive_index]

    selected = (
        "small" if probability >= threshold
        else "strong"
    )

    return selected, float(probability)


if __name__ == "__main__":
    train_router()
