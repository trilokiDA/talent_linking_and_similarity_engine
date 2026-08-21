"""
Utility script to inspect and analyze stakeholder data in the data lake
"""

import json
from pathlib import Path
from collections import Counter
from datetime import datetime


def load_stakeholder_data(source, year, month, day):
    """Load stakeholder data from data lake"""
    file_path = Path(f"data-lake/{source}/{year}/{month:02d}/{day:02d}/stakeholder.json")

    if not file_path.exists():
        print(f"File not found: {file_path}")
        return []

    with open(file_path, 'r') as f:
        return json.load(f)


def analyze_profiles(profiles, source_name):
    """Generate statistics about the profiles"""
    print(f"\n{'='*60}")
    print(f"{source_name.upper()} PROFILE ANALYSIS")
    print(f"{'='*60}")

    print(f"\nTotal Profiles: {len(profiles)}")

    if not profiles:
        return

    # Institution distribution
    if source_name == "coresignal":
        institutions = [p['current_company'] for p in profiles]
        print("\nTop 10 Institutions:")
        for inst, count in Counter(institutions).most_common(10):
            print(f"  {inst}: {count}")

        # Title distribution
        titles = [p['title'] for p in profiles]
        print("\nTop 10 Titles:")
        for title, count in Counter(titles).most_common(10):
            print(f"  {title}: {count}")

        # Department distribution
        departments = [p['department'] for p in profiles]
        print("\nTop 10 Departments:")
        for dept, count in Counter(departments).most_common(10):
            print(f"  {dept}: {count}")

        # H-index statistics
        h_indices = [p['h_index'] for p in profiles]
        print(f"\nH-Index Statistics:")
        print(f"  Average: {sum(h_indices) / len(h_indices):.2f}")
        print(f"  Min: {min(h_indices)}")
        print(f"  Max: {max(h_indices)}")

        # Citation statistics
        citations = [p['total_citations'] for p in profiles]
        print(f"\nCitation Statistics:")
        print(f"  Average: {sum(citations) / len(citations):.0f}")
        print(f"  Min: {min(citations)}")
        print(f"  Max: {max(citations)}")

    elif source_name == "rocketreach":
        employers = [p['current_employer'] for p in profiles]
        print("\nTop 10 Employers:")
        for emp, count in Counter(employers).most_common(10):
            print(f"  {emp}: {count}")

        # Email verification
        verified = sum(1 for p in profiles if p.get('verified_email', False))
        print(f"\nEmail Verification:")
        print(f"  Verified: {verified} ({verified/len(profiles)*100:.1f}%)")
        print(f"  Unverified: {len(profiles)-verified} ({(len(profiles)-verified)/len(profiles)*100:.1f}%)")

        # Social profile presence
        linkedin = sum(1 for p in profiles if p['social_profiles'].get('linkedin'))
        twitter = sum(1 for p in profiles if p['social_profiles'].get('twitter'))
        scholar = sum(1 for p in profiles if p['social_profiles'].get('google_scholar'))
        orcid = sum(1 for p in profiles if p['social_profiles'].get('orcid'))

        print(f"\nSocial Profile Coverage:")
        print(f"  LinkedIn: {linkedin} ({linkedin/len(profiles)*100:.1f}%)")
        print(f"  Twitter: {twitter} ({twitter/len(profiles)*100:.1f}%)")
        print(f"  Google Scholar: {scholar} ({scholar/len(profiles)*100:.1f}%)")
        print(f"  ORCID: {orcid} ({orcid/len(profiles)*100:.1f}%)")

        # Research areas
        all_areas = []
        for p in profiles:
            all_areas.extend(p.get('research_areas', []))

        print(f"\nTop 10 Research Areas:")
        for area, count in Counter(all_areas).most_common(10):
            print(f"  {area}: {count}")

        # Publication statistics
        pub_counts = [p.get('total_publications', 0) for p in profiles]
        print(f"\nPublication Statistics:")
        print(f"  Average: {sum(pub_counts) / len(pub_counts):.1f}")
        print(f"  Min: {min(pub_counts)}")
        print(f"  Max: {max(pub_counts)}")


def show_sample_profile(profiles, source_name, index=0):
    """Display a sample profile"""
    if not profiles or index >= len(profiles):
        return

    print(f"\n{'='*60}")
    print(f"SAMPLE {source_name.upper()} PROFILE #{index+1}")
    print(f"{'='*60}")
    print(json.dumps(profiles[index], indent=2))


def compare_sources():
    """Compare data between CoreSignal and RocketReach"""
    today = datetime.now()
    year = today.year
    month = today.month
    day = today.day

    cs_profiles = load_stakeholder_data("coresignal", year, month, day)
    rr_profiles = load_stakeholder_data("rocketreach", year, month, day)

    print(f"\n{'='*60}")
    print("DATA SOURCE COMPARISON")
    print(f"{'='*60}")

    print(f"\nDate: {year}-{month:02d}-{day:02d}")
    print(f"\nCoreSignal:")
    print(f"  Profiles: {len(cs_profiles)}")
    print(f"  Focus: Employment history, career trajectory")
    print(f"  Key strengths: Detailed work experience, education history")

    print(f"\nRocketReach:")
    print(f"  Profiles: {len(rr_profiles)}")
    print(f"  Focus: Contact information, social profiles, publications")
    print(f"  Key strengths: Email/phone contacts, publication records, ORCID IDs")

    print(f"\nData Completeness:")

    # CoreSignal completeness
    if cs_profiles:
        cs_avg_completeness = sum(p.get('profile_completeness', 0) for p in cs_profiles) / len(cs_profiles)
        print(f"  CoreSignal avg completeness: {cs_avg_completeness:.1f}%")

    # RocketReach completeness (based on confidence score)
    if rr_profiles:
        rr_avg_confidence = sum(p.get('confidence_score', 0) for p in rr_profiles) / len(rr_profiles)
        print(f"  RocketReach avg confidence: {rr_avg_confidence:.2f}")


def main():
    """Main inspection routine"""
    today = datetime.now()
    year = today.year
    month = today.month
    day = today.day

    print("="*60)
    print("ATLAS DATA LAKE INSPECTOR")
    print("="*60)
    print(f"\nInspecting data for: {year}-{month:02d}-{day:02d}\n")

    # Load data
    cs_profiles = load_stakeholder_data("coresignal", year, month, day)
    rr_profiles = load_stakeholder_data("rocketreach", year, month, day)

    # Analyze each source
    if cs_profiles:
        analyze_profiles(cs_profiles, "coresignal")
        show_sample_profile(cs_profiles, "coresignal", 0)

    if rr_profiles:
        analyze_profiles(rr_profiles, "rocketreach")
        show_sample_profile(rr_profiles, "rocketreach", 0)

    # Compare sources
    compare_sources()

    print("\n" + "="*60)
    print("INSPECTION COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
