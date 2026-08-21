import os
import json
import glob
from pathlib import Path

def get_linkedin_username(url):
    if not url:
        return None
    # e.g., linkedin.com/in/weidavis674 or https://linkedin.com/in/ahmedliu
    url = url.strip().rstrip('/')
    return url.split('/')[-1]

def normalize_coresignal(input_file, output_dir):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for item in data:
        person_id = item.get('person_id')
        if not person_id:
            continue
            
        location = item.get('location', '')
        country = item.get('country', '')
        full_address = f"{location}, {country}".strip(", ")
        
        normalized = {
            "id": person_id,
            "full_name": item.get('full_name'),
            "current_employer": item.get('current_company'),
            "title": item.get('title'),
            "linkedin_username": get_linkedin_username(item.get('linkedin_url')),
            "full_adress": full_address,  # user explicitly spelled it as full_adress
            "contact_number": None  # CoreSignal data shown doesn't have phones
        }
        
        output_file = os.path.join(output_dir, f"{person_id}.json")
        with open(output_file, 'w', encoding='utf-8') as out_f:
            json.dump(normalized, out_f, indent=2)

def normalize_rocketreach(input_file, output_dir):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for item in data:
        person_id = item.get('id')
        if not person_id:
            continue
            
        loc = item.get('location', {})
        city = loc.get('city', '')
        state = loc.get('state', '')
        country = loc.get('country', '')
        full_address = ", ".join(filter(None, [city, state, country]))
        
        phones = item.get('phones', [])
        contact_number = phones[0] if phones else None
        
        socials = item.get('social_profiles', {})
        linkedin = socials.get('linkedin')
        
        normalized = {
            "id": person_id,
            "full_name": item.get('name'),
            "current_employer": item.get('current_employer'),
            "title": item.get('current_title'),
            "linkedin_username": get_linkedin_username(linkedin),
            "full_adress": full_address,
            "contact_number": contact_number
        }
        
        output_file = os.path.join(output_dir, f"{person_id}.json")
        with open(output_file, 'w', encoding='utf-8') as out_f:
            json.dump(normalized, out_f, indent=2)

def main():
    base_dir = Path("D:/Project/atlas/talent_linking_and_similarity_engine")
    data_lake = base_dir / "data-lake"
    
    # Create output directories
    coresignal_out = base_dir / "processed-data" / "normalization" / "coresignal"
    rocketreach_out = base_dir / "processed-data" / "normalization" / "rocketreach"
    
    coresignal_out.mkdir(parents=True, exist_ok=True)
    rocketreach_out.mkdir(parents=True, exist_ok=True)
    
    # Process CoreSignal files
    print("Processing CoreSignal...")
    for file_path in data_lake.glob("coresignal/**/*.json"):
        normalize_coresignal(file_path, coresignal_out)
        
    # Process RocketReach files
    print("Processing RocketReach...")
    for file_path in data_lake.glob("rocketreach/**/*.json"):
        normalize_rocketreach(file_path, rocketreach_out)
        
    print("Normalization complete.")

if __name__ == "__main__":
    main()
