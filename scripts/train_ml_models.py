import json
import pickle
from pathlib import Path
from ml_matching import NameEmbedder, LocationEmbedder, load_config

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
    models_dir = base_dir / "models" / "embeddings"

    # Load configuration
    config = load_config()
    print("Loaded configuration from ml_config.yaml")

    # Load all CoreSignal and RocketReach profiles
    print("\nLoading training data...")
    cs_profiles = load_all_profiles(norm_dir / "coresignal")
    rr_profiles = load_all_profiles(norm_dir / "rocketreach")

    all_profiles = cs_profiles + rr_profiles
    print(f"Loaded {len(cs_profiles)} CoreSignal profiles")
    print(f"Loaded {len(rr_profiles)} RocketReach profiles")
    print(f"Total training profiles: {len(all_profiles)}")

    # Extract names and locations
    names = [p.get('full_name', '') for p in all_profiles]
    locations = [p.get('full_adress', '') for p in all_profiles]

    # Train name embedder
    print("\nTraining name embedder...")
    name_embedder = NameEmbedder(config)
    name_embedder.fit(names)
    print("Name embedder trained successfully")

    # Save name embedder
    name_tfidf_path = models_dir / "name_tfidf_vectorizer.pkl"
    name_svd_path = models_dir / "name_svd_model.pkl"

    models_dir.mkdir(parents=True, exist_ok=True)

    with open(name_tfidf_path, 'wb') as f:
        pickle.dump(name_embedder.tfidf_vectorizer, f)

    with open(name_svd_path, 'wb') as f:
        pickle.dump(name_embedder.svd, f)

    print(f"Saved name TF-IDF vectorizer to {name_tfidf_path}")
    print(f"Saved name SVD model to {name_svd_path}")

    # Train location embedder
    print("\nTraining location embedder...")
    location_embedder = LocationEmbedder(config)
    location_embedder.fit(locations)
    print("Location embedder trained successfully")

    # Save location embedder
    location_tfidf_path = models_dir / "location_tfidf_vectorizer.pkl"
    location_svd_path = models_dir / "location_svd_model.pkl"

    with open(location_tfidf_path, 'wb') as f:
        pickle.dump(location_embedder.tfidf_vectorizer, f)

    with open(location_svd_path, 'wb') as f:
        pickle.dump(location_embedder.svd, f)

    print(f"Saved location TF-IDF vectorizer to {location_tfidf_path}")
    print(f"Saved location SVD model to {location_svd_path}")

    print("\nModel training complete!")
    print("\nNext steps:")
    print("1. Download FastText model: cc.en.100.bin")
    print("   URL: https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.en.100.bin.gz")
    print("   Extract to: models/fasttext/cc.en.100.bin")
    print("2. Run hybrid_matching.py to perform ML-based matching")

if __name__ == "__main__":
    main()
