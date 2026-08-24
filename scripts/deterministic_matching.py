import os
import json
from pathlib import Path

def build_lookup_index(data_dir):
    """
    Builds lookup dictionaries for linkedin_username and contact_number.
    """
    linkedin_idx = {}
    phone_idx = {}
    
    if not data_dir.exists():
        return linkedin_idx, phone_idx
        
    for file_path in data_dir.glob("*.json"):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            linkedin = data.get('linkedin_username')
            if linkedin:
                linkedin_idx[linkedin.lower()] = data
                
            phone = data.get('contact_number')
            if phone:
                phone_idx[phone] = data
                
    return linkedin_idx, phone_idx

def match_profile(borealis_data, rr_indexes, cs_indexes):
    """
    Matches a borealis profile deterministically against RocketReach then CoreSignal.
    Returns the matched profile data and source, or None if no match.
    """
    linkedin = borealis_data.get('linkedin_username')
    phone = borealis_data.get('contact_number')
    
    if linkedin:
        linkedin = linkedin.lower()
    
    rr_linkedin_idx, rr_phone_idx = rr_indexes
    cs_linkedin_idx, cs_phone_idx = cs_indexes
    
    # 1. Try matching with RocketReach
    if phone and phone in rr_phone_idx:
        return rr_phone_idx[phone], "rocketreach"
    if linkedin and linkedin in rr_linkedin_idx:
        return rr_linkedin_idx[linkedin], "rocketreach"
        
    # 2. Try matching with CoreSignal if not found in RocketReach
    if phone and phone in cs_phone_idx:
        return cs_phone_idx[phone], "coresignal"
    if linkedin and linkedin in cs_linkedin_idx:
        return cs_linkedin_idx[linkedin], "coresignal"
        
    return None, None

def main():
    # Use current working directory as base
    base_dir = Path(__file__).parent.parent
    norm_dir = base_dir / "processed-data" / "normalization"
    
    borealis_dir = norm_dir / "borealis"
    rr_dir = norm_dir / "rocketreach"
    cs_dir = norm_dir / "coresignal"
    
    matched_dir = base_dir / "processed-data" / "matched"
    matched_dir.mkdir(parents=True, exist_ok=True)
    
    print("Building RocketReach indexes...")
    rr_indexes = build_lookup_index(rr_dir)
    
    print("Building CoreSignal indexes...")
    cs_indexes = build_lookup_index(cs_dir)
    
    print("Matching Borealis profiles...")
    match_count = 0
    
    for b_file in borealis_dir.glob("*.json"):
        with open(b_file, 'r', encoding='utf-8') as f:
            b_data = json.load(f)
            
        matched_data, source = match_profile(b_data, rr_indexes, cs_indexes)
        
        if matched_data:
            # Create a combined matched profile
            # We keep the base borealis info and add match info and enrich missing attributes
            enriched_profile = b_data.copy()
            
            # Enrich missing fields from the matched profile
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
            
            output_file = matched_dir / b_file.name
            with open(output_file, 'w', encoding='utf-8') as out_f:
                json.dump(enriched_profile, out_f, indent=2)
                
            match_count += 1
            print(f"Matched {b_data.get('id')} with {source} ({matched_data.get('id')})")
            
    print(f"Deterministic matching complete. Matched {match_count} profiles.")

if __name__ == "__main__":
    main()
