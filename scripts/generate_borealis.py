import os
import json
import random
from pathlib import Path

def main():
    base_dir = Path("D:/Project/atlas/talent_linking_and_similarity_engine")
    cs_dir = base_dir / "processed-data" / "normalization" / "coresignal"
    rr_dir = base_dir / "processed-data" / "normalization" / "rocketreach"
    
    borealis_out_dir = base_dir / "data-lake" / "borealis" / "2026" / "08" / "22"
    borealis_out_dir.mkdir(parents=True, exist_ok=True)
    
    profiles = []
    
    # Get 4 CoreSignal profiles
    cs_files = list(cs_dir.glob("*.json"))[:4]
    for i, f in enumerate(cs_files):
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            profiles.append({
                "source": "borealis",
                "b_id": f"BOR_{100+i}",
                "name": data.get("full_name"),
                "company": data.get("current_employer"),
                "position": data.get("title"),
                "linkedin": f"linkedin.com/in/{data.get('linkedin_username')}" if data.get('linkedin_username') else None,
                "location": data.get("full_adress"),
                "phone": data.get("contact_number")
            })

    # Get 4 RocketReach profiles
    rr_files = list(rr_dir.glob("*.json"))[:4]
    for i, f in enumerate(rr_files):
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            profiles.append({
                "source": "borealis",
                "b_id": f"BOR_{200+i}",
                "name": data.get("full_name"),
                "company": data.get("current_employer"),
                "position": data.get("title"),
                "linkedin": f"linkedin.com/in/{data.get('linkedin_username')}" if data.get('linkedin_username') else None,
                "location": data.get("full_adress"),
                "phone": data.get("contact_number")
            })

    # Add 2 random profiles
    random_profiles = [
        {
            "source": "borealis",
            "b_id": "BOR_300",
            "name": "Alice Johnson",
            "company": "Tech Innovations Inc.",
            "position": "Software Engineer",
            "linkedin": "linkedin.com/in/alicej",
            "location": "San Francisco, CA, USA",
            "phone": "+1-555-0192"
        },
        {
            "source": "borealis",
            "b_id": "BOR_301",
            "name": "Bob Smith",
            "company": "Global Solutions Ltd.",
            "position": "Product Manager",
            "linkedin": "linkedin.com/in/bobsmith",
            "location": "London, UK",
            "phone": "+44-20-7123-4567"
        }
    ]
    
    profiles.extend(random_profiles)
    
    # Shuffle for realism
    random.shuffle(profiles)
    
    output_file = borealis_out_dir / "stakeholder.json"
    with open(output_file, 'w', encoding='utf-8') as out_f:
        json.dump(profiles, out_f, indent=2)
        
    print(f"Created {len(profiles)} profiles in {output_file}")

if __name__ == "__main__":
    main()
