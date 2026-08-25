import json
from pathlib import Path
from gensim.models import FastText
import re

def preprocess_text(text):
    if not text:
        return []
    # Lowercase and split into words
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    words = text.split()
    return words

def load_all_profiles(data_dir):
    profiles = []
    if not data_dir.exists():
        return profiles

    for file_path in data_dir.glob("*.json"):
        with open(file_path, 'r', encoding='utf-8') as f:
            profiles.append(json.load(f))

    return profiles

def main():
    base_dir = Path(__file__).parent.parent
    norm_dir = base_dir / "processed-data" / "normalization"
    models_dir = base_dir / "models" / "fasttext"
    models_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("TRAINING FASTTEXT MODEL ON ATLAS DATA")
    print("=" * 70)

    # Load all profiles
    print("\nLoading profiles...")
    cs_profiles = load_all_profiles(norm_dir / "coresignal")
    rr_profiles = load_all_profiles(norm_dir / "rocketreach")
    borealis_profiles = load_all_profiles(norm_dir / "borealis")

    all_profiles = cs_profiles + rr_profiles + borealis_profiles
    print(f"Loaded {len(all_profiles)} total profiles")

    # Extract and tokenize all text
    print("\nExtracting and tokenizing text...")
    sentences = []

    for profile in all_profiles:
        # Names
        name = profile.get('full_name', '')
        if name:
            sentences.append(preprocess_text(name))

        # Locations
        location = profile.get('full_adress', '')
        if location:
            sentences.append(preprocess_text(location))

        # Employers
        employer = profile.get('current_employer', '')
        if employer:
            sentences.append(preprocess_text(employer))

        # Titles
        title = profile.get('title', '')
        if title:
            sentences.append(preprocess_text(title))

    sentences = [s for s in sentences if s]  # Remove empty
    print(f"Created {len(sentences)} training sentences")

    # Train FastText model
    print("\nTraining FastText model...")
    print("  Vector size: 100")
    print("  Window size: 5")
    print("  Min count: 1")
    print("  Workers: 4")

    model = FastText(
        sentences=sentences,
        vector_size=100,
        window=5,
        min_count=1,
        workers=4,
        epochs=10,
        sg=1  # Skip-gram
    )

    print("FastText model trained successfully")

    # Save model
    model_path = models_dir / "cc.en.100.bin"
    model.save(str(model_path))
    print(f"\nModel saved to: {model_path}")

    # Show some statistics
    print("\n" + "-" * 70)
    print("MODEL STATISTICS")
    print("-" * 70)
    print(f"Vocabulary size: {len(model.wv)}")
    print(f"Vector dimensions: {model.wv.vector_size}")

    # Test some similarities
    test_words = ['professor', 'director', 'california', 'university']
    print("\nSample word similarities:")
    for word in test_words:
        if word in model.wv:
            similar = model.wv.most_similar(word, topn=3)
            print(f"\n  '{word}' is similar to:")
            for sim_word, score in similar:
                print(f"    - {sim_word}: {score:.3f}")

    print("\n" + "=" * 70)
    print("FASTTEXT TRAINING COMPLETE")
    print("=" * 70)
    print("\nNext step: Run python scripts/train_ml_models.py")

if __name__ == "__main__":
    main()
