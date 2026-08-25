import json
from pathlib import Path
from collections import Counter

def load_matched_profiles(matched_dir):
    profiles = []
    if not matched_dir.exists():
        return profiles

    for file_path in matched_dir.glob("*.json"):
        with open(file_path, 'r', encoding='utf-8') as f:
            profiles.append(json.load(f))

    return profiles

def main():
    base_dir = Path(__file__).parent.parent
    matched_dir = base_dir / "processed-data" / "matched"

    print("=" * 70)
    print("ATLAS ML MATCHING VALIDATION")
    print("=" * 70)

    # Load all matched profiles
    matched_profiles = load_matched_profiles(matched_dir)

    if not matched_profiles:
        print("\nNo matched profiles found.")
        print("Run hybrid_matching.py first to generate matches.")
        return

    print(f"\nTotal matched profiles: {len(matched_profiles)}")

    # Categorize by match type
    match_types = Counter()
    sources = Counter()
    ml_matches = []
    deterministic_matches = []

    for profile in matched_profiles:
        match_info = profile.get('match_info', {})
        match_type = match_info.get('match_type', 'unknown')
        source = match_info.get('source', 'unknown')

        match_types[match_type] += 1
        sources[source] += 1

        if match_type == 'ml_embedding':
            ml_matches.append(profile)
        elif match_type == 'deterministic':
            deterministic_matches.append(profile)

    # Summary statistics
    print("\n" + "-" * 70)
    print("MATCH TYPE DISTRIBUTION")
    print("-" * 70)
    for match_type, count in match_types.most_common():
        percentage = 100 * count / len(matched_profiles)
        print(f"  {match_type:20s}: {count:3d} ({percentage:5.1f}%)")

    print("\n" + "-" * 70)
    print("SOURCE DISTRIBUTION")
    print("-" * 70)
    for source, count in sources.most_common():
        percentage = 100 * count / len(matched_profiles)
        print(f"  {source:20s}: {count:3d} ({percentage:5.1f}%)")

    # Detailed ML match analysis
    if ml_matches:
        print("\n" + "=" * 70)
        print("ML MATCH DETAILS")
        print("=" * 70)

        confidence_scores = [m['match_info']['confidence_score'] for m in ml_matches]
        name_similarities = [m['match_info']['name_similarity'] for m in ml_matches]
        location_similarities = [m['match_info']['location_similarity'] for m in ml_matches]

        print(f"\nNumber of ML matches: {len(ml_matches)}")
        print(f"\nConfidence Score Statistics:")
        print(f"  Min:  {min(confidence_scores):.3f}")
        print(f"  Max:  {max(confidence_scores):.3f}")
        print(f"  Mean: {sum(confidence_scores)/len(confidence_scores):.3f}")

        print(f"\nName Similarity Statistics:")
        print(f"  Min:  {min(name_similarities):.3f}")
        print(f"  Max:  {max(name_similarities):.3f}")
        print(f"  Mean: {sum(name_similarities)/len(name_similarities):.3f}")

        print(f"\nLocation Similarity Statistics:")
        print(f"  Min:  {min(location_similarities):.3f}")
        print(f"  Max:  {max(location_similarities):.3f}")
        print(f"  Mean: {sum(location_similarities)/len(location_similarities):.3f}")

        # Show each ML match in detail
        print("\n" + "-" * 70)
        print("INDIVIDUAL ML MATCHES")
        print("-" * 70)

        for i, profile in enumerate(ml_matches, 1):
            match_info = profile['match_info']

            print(f"\n[{i}] Borealis Profile: {profile['id']}")
            print(f"    Name:     {profile.get('full_name', 'N/A')}")
            print(f"    Employer: {profile.get('current_employer', 'N/A')}")
            print(f"    Location: {profile.get('full_adress', 'N/A')}")

            print(f"\n    Matched with: {match_info['matched_id']} ({match_info['source']})")
            print(f"    Confidence Score:     {match_info['confidence_score']:.3f}")
            print(f"    Name Similarity:      {match_info['name_similarity']:.3f}")
            print(f"    Location Similarity:  {match_info['location_similarity']:.3f}")

    else:
        print("\n" + "=" * 70)
        print("No ML matches found.")
        print("All matches were made using deterministic rules.")

    # Deterministic match summary
    if deterministic_matches:
        print("\n" + "=" * 70)
        print("DETERMINISTIC MATCH SUMMARY")
        print("=" * 70)
        print(f"Number of deterministic matches: {len(deterministic_matches)}")

        det_sources = Counter(m['match_info']['source'] for m in deterministic_matches)
        print("\nBy source:")
        for source, count in det_sources.most_common():
            print(f"  {source:20s}: {count:3d}")

    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
