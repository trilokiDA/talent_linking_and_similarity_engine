import json
import pickle
from pathlib import Path
from gensim.models import FastText
from deterministic_matching import build_lookup_index, match_profile
from ml_matching import NameEmbedder, LocationEmbedder, find_best_match, load_config

def load_ml_models(config):
    base_dir = Path(__file__).parent.parent
    models_dir = base_dir / "models" / "embeddings"

    # Load name embedder components
    name_embedder = NameEmbedder(config)
    with open(models_dir / "name_tfidf_vectorizer.pkl", 'rb') as f:
        name_embedder.tfidf_vectorizer = pickle.load(f)
    with open(models_dir / "name_svd_model.pkl", 'rb') as f:
        name_embedder.svd = pickle.load(f)

    # Load location embedder components
    location_embedder = LocationEmbedder(config)
    with open(models_dir / "location_tfidf_vectorizer.pkl", 'rb') as f:
        location_embedder.tfidf_vectorizer = pickle.load(f)
    with open(models_dir / "location_svd_model.pkl", 'rb') as f:
        location_embedder.svd = pickle.load(f)

    return name_embedder, location_embedder

def load_fasttext_model(config):
    base_dir = Path(__file__).parent.parent
    model_path = base_dir / config['fasttext']['model_path']

    if not model_path.exists():
        raise FileNotFoundError(
            f"FastText model not found at {model_path}\n"
            f"For now, you can train a simple model or skip FastText.\n"
            f"To use pre-trained: download from {config['fasttext'].get('download_url', 'FastText website')}"
        )

    print(f"Loading FastText model from {model_path}...")
    model = FastText.load(str(model_path))
    print("FastText model loaded successfully")
    return model

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
    matched_dir = base_dir / "processed-data" / "matched"
    matched_dir.mkdir(parents=True, exist_ok=True)

    borealis_dir = norm_dir / "borealis"
    rr_dir = norm_dir / "rocketreach"
    cs_dir = norm_dir / "coresignal"

    # Load configuration
    config = load_config()
    print("=" * 60)
    print("ATLAS HYBRID MATCHING PIPELINE")
    print("=" * 60)

    # Phase 1: Deterministic Matching
    print("\nPHASE 1: DETERMINISTIC MATCHING")
    print("-" * 60)

    print("Building RocketReach indexes...")
    rr_indexes = build_lookup_index(rr_dir)

    print("Building CoreSignal indexes...")
    cs_indexes = build_lookup_index(cs_dir)

    print("Matching Borealis profiles using deterministic rules...")
    deterministic_matches = []
    unmatched_profiles = []

    for b_file in borealis_dir.glob("*.json"):
        with open(b_file, 'r', encoding='utf-8') as f:
            b_data = json.load(f)

        matched_data, source = match_profile(b_data, rr_indexes, cs_indexes)

        if matched_data:
            enriched_profile = b_data.copy()

            # Enrich missing fields
            for key, value in matched_data.items():
                if not enriched_profile.get(key) and value:
                    enriched_profile[key] = value

            # Add match metadata
            enriched_profile['match_info'] = {
                'matched': True,
                'match_type': 'deterministic',
                'source': source,
                'matched_id': matched_data.get('id')
            }

            deterministic_matches.append(enriched_profile)

            # Save deterministic match
            output_file = matched_dir / b_file.name
            with open(output_file, 'w', encoding='utf-8') as out_f:
                json.dump(enriched_profile, out_f, indent=2)

            print(f"[OK] Matched {b_data.get('id')} with {source} ({matched_data.get('id')})")
        else:
            unmatched_profiles.append(b_data)
            print(f"[X] No deterministic match for {b_data.get('id')}")

    print(f"\nDeterministic matching results: {len(deterministic_matches)}/{len(list(borealis_dir.glob('*.json')))} matched")

    # Phase 2: ML Matching
    if unmatched_profiles:
        print("\n" + "=" * 60)
        print("PHASE 2: ML-BASED MATCHING")
        print("-" * 60)
        print(f"Attempting ML matching for {len(unmatched_profiles)} unmatched profiles...")

        try:
            # Load ML models
            print("\nLoading ML models...")
            name_embedder, location_embedder = load_ml_models(config)
            print("ML models loaded successfully")

            # Load FastText model
            fasttext_model = load_fasttext_model(config)

            # Load all candidate profiles
            print("\nLoading candidate profiles...")
            cs_candidates = load_all_profiles(cs_dir)
            rr_candidates = load_all_profiles(rr_dir)
            all_candidates = cs_candidates + rr_candidates
            print(f"Loaded {len(all_candidates)} candidate profiles")

            # Perform ML matching
            ml_match_count = 0
            threshold = config['matching']['similarity_threshold']

            print(f"\nMatching with threshold = {threshold}")
            print("-" * 60)

            for b_profile in unmatched_profiles:
                print(f"\nProcessing {b_profile.get('id')}:")
                print(f"  Name: {b_profile.get('full_name')}")
                print(f"  Location: {b_profile.get('full_adress')}")

                best_match, score_info = find_best_match(
                    b_profile, all_candidates,
                    name_embedder, location_embedder,
                    fasttext_model, config
                )

                if best_match:
                    # Create enriched profile
                    enriched_profile = b_profile.copy()

                    # Enrich missing fields
                    for key, value in best_match.items():
                        if not enriched_profile.get(key) and value:
                            enriched_profile[key] = value

                    # Determine source
                    source = "coresignal" if best_match['id'].startswith('CS_') else "rocketreach"

                    # Add ML match metadata
                    enriched_profile['match_info'] = {
                        'matched': True,
                        'match_type': 'ml_embedding',
                        'source': source,
                        'matched_id': best_match.get('id'),
                        'confidence_score': score_info['final_score'],
                        'name_similarity': score_info['name_similarity'],
                        'location_similarity': score_info['location_similarity']
                    }

                    # Save ML match
                    output_file = matched_dir / f"{b_profile['id']}.json"
                    with open(output_file, 'w', encoding='utf-8') as out_f:
                        json.dump(enriched_profile, out_f, indent=2)

                    ml_match_count += 1
                    print(f"  [OK] ML match found: {best_match.get('id')} from {source}")
                    print(f"    Confidence: {score_info['final_score']:.3f}")
                    print(f"    Name sim: {score_info['name_similarity']:.3f}, Location sim: {score_info['location_similarity']:.3f}")
                else:
                    print(f"  [X] No match found above threshold {threshold}")

                    # Show top 3 candidates for debugging
                    print(f"  Top 3 candidates (below threshold):")
                    scores = []
                    for candidate in all_candidates[:50]:  # Check top 50 to speed up
                        score_info_temp = name_embedder.transform_hybrid([b_profile.get('full_name', '')], fasttext_model)
                        # Simple approximation for debugging
                        from ml_matching import compute_profile_similarity
                        score_info_temp = compute_profile_similarity(
                            b_profile, candidate,
                            name_embedder, location_embedder,
                            fasttext_model, config
                        )
                        scores.append((candidate, score_info_temp))

                    scores.sort(key=lambda x: x[1]['final_score'], reverse=True)
                    for i, (cand, score_info_temp) in enumerate(scores[:3], 1):
                        print(f"    {i}. {cand.get('id')} - {cand.get('full_name')} ({cand.get('full_adress')})")
                        print(f"       Score: {score_info_temp['final_score']:.3f} (name: {score_info_temp['name_similarity']:.3f}, loc: {score_info_temp['location_similarity']:.3f})")

            print("\n" + "=" * 60)
            print(f"ML matching results: {ml_match_count}/{len(unmatched_profiles)} matched")

        except FileNotFoundError as e:
            print(f"\n[WARNING] Warning: {e}")
            print("ML matching skipped. Please download the FastText model to enable ML matching.")
        except Exception as e:
            print(f"\n[WARNING] Error during ML matching: {e}")
            print("ML matching failed. Check error details above.")

    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    total_profiles = len(list(borealis_dir.glob('*.json')))
    total_matched = len(list(matched_dir.glob('*.json')))
    print(f"Total Borealis profiles: {total_profiles}")
    print(f"Total matched (deterministic + ML): {total_matched}")
    print(f"Match rate: {total_matched}/{total_profiles} ({100*total_matched/total_profiles:.1f}%)")
    print("\nMatched profiles saved to: processed-data/matched/")

if __name__ == "__main__":
    main()
