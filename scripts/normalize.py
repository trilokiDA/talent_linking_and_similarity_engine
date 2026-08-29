import os
import json
import glob
from datetime import date
from pathlib import Path


def get_latest_date_path(source_dir: Path) -> Path | None:
    """Return the Path to the latest YYYY/MM/DD partition under *source_dir*.

    The data-lake follows the layout::

        data-lake/<source>/YYYY/MM/DD/<files>.json

    This function scans all ``YYYY/MM/DD`` leaf directories, converts each
    to a :class:`datetime.date` for reliable chronological comparison, and
    returns the one corresponding to the most recent date.

    Args:
        source_dir: Root directory for a single data source, e.g.
                    ``data-lake/coresignal``.

    Returns:
        A :class:`~pathlib.Path` pointing to the latest date folder, or
        ``None`` when *source_dir* does not exist or contains no valid
        ``YYYY/MM/DD`` partitions.

    Example::

        latest = get_latest_date_path(base_dir / "data-lake" / "coresignal")
        if latest:
            print(f"Processing snapshot from {latest}")
    """
    if not source_dir.exists():
        return None

    latest_date: date | None = None
    latest_path: Path | None = None

    # Walk every YYYY/MM/DD sub-directory.  glob("*/*/**") is intentionally
    # kept as three levels so we don't accidentally pick up deeper artefacts.
    for year_dir in sorted(source_dir.iterdir()):
        if not year_dir.is_dir():
            continue
        for month_dir in sorted(year_dir.iterdir()):
            if not month_dir.is_dir():
                continue
            for day_dir in sorted(month_dir.iterdir()):
                if not day_dir.is_dir():
                    continue
                try:
                    partition_date = date(
                        int(year_dir.name),
                        int(month_dir.name),
                        int(day_dir.name),
                    )
                except ValueError:
                    # Skip directories whose names aren't valid date components.
                    continue

                if latest_date is None or partition_date > latest_date:
                    latest_date = partition_date
                    latest_path = day_dir

    return latest_path


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

def normalize_borealis(input_file, output_dir):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for item in data:
        person_id = item.get('b_id')
        if not person_id:
            continue
            
        normalized = {
            "id": person_id,
            "full_name": item.get('name'),
            "current_employer": item.get('company'),
            "title": item.get('position'),
            "linkedin_username": get_linkedin_username(item.get('linkedin')),
            "full_adress": item.get('location'),
            "contact_number": item.get('phone')
        }
        
        output_file = os.path.join(output_dir, f"{person_id}.json")
        with open(output_file, 'w', encoding='utf-8') as out_f:
            json.dump(normalized, out_f, indent=2)

def main():
    # Use current working directory as base
    base_dir = Path(__file__).parent.parent
    data_lake = base_dir / "data-lake"

    # Create output directories
    coresignal_out = base_dir / "processed-data" / "normalization" / "coresignal"
    rocketreach_out = base_dir / "processed-data" / "normalization" / "rocketreach"
    borealis_out = base_dir / "processed-data" / "normalization" / "borealis"

    coresignal_out.mkdir(parents=True, exist_ok=True)
    rocketreach_out.mkdir(parents=True, exist_ok=True)
    borealis_out.mkdir(parents=True, exist_ok=True)

    # --- CoreSignal ---
    print("Processing CoreSignal...")
    cs_latest = get_latest_date_path(data_lake / "coresignal")
    if cs_latest:
        print(f"  Latest snapshot: {cs_latest}")
        for file_path in cs_latest.glob("*.json"):
            normalize_coresignal(file_path, coresignal_out)
    else:
        print("  [WARNING] No CoreSignal date partitions found – skipping.")

    # --- RocketReach ---
    print("Processing RocketReach...")
    rr_latest = get_latest_date_path(data_lake / "rocketreach")
    if rr_latest:
        print(f"  Latest snapshot: {rr_latest}")
        for file_path in rr_latest.glob("*.json"):
            normalize_rocketreach(file_path, rocketreach_out)
    else:
        print("  [WARNING] No RocketReach date partitions found – skipping.")

    # --- Borealis ---
    print("Processing Borealis...")
    bo_latest = get_latest_date_path(data_lake / "borealis")
    if bo_latest:
        print(f"  Latest snapshot: {bo_latest}")
        for file_path in bo_latest.glob("*.json"):
            normalize_borealis(file_path, borealis_out)
    else:
        print("  [WARNING] No Borealis date partitions found – skipping.")

    print("Normalization complete.")

if __name__ == "__main__":
    main()
