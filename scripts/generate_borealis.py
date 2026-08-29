import json
import random
from datetime import date
from pathlib import Path

# Re-use the shared utility from normalize.py
from normalize import get_latest_date_path


# ---------------------------------------------------------------------------
# Helpers to read raw data-lake records
# ---------------------------------------------------------------------------

def _load_records(date_dir: Path) -> list[dict]:
    """Return all JSON records from every *.json file inside *date_dir*."""
    records = []
    for json_file in sorted(date_dir.glob("*.json")):
        with open(json_file, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
            # Each file may contain a single record (dict) or a list of records.
            if isinstance(payload, list):
                records.extend(payload)
            elif isinstance(payload, dict):
                records.append(payload)
    return records


def _coresignal_to_borealis(record: dict, b_id: str) -> dict:
    """Map a raw CoreSignal record to the Borealis schema."""
    location = record.get("location", "")
    country = record.get("country", "")
    full_location = ", ".join(filter(None, [location, country]))

    linkedin_url = record.get("linkedin_url")
    if linkedin_url:
        linkedin_username = linkedin_url.strip().rstrip("/").split("/")[-1]
        linkedin = f"linkedin.com/in/{linkedin_username}"
    else:
        linkedin = None

    return {
        "source": "borealis",
        "b_id": b_id,
        "name": record.get("full_name"),
        "company": record.get("current_company"),
        "position": record.get("title"),
        "linkedin": linkedin,
        "location": full_location or None,
        "phone": None,  # CoreSignal raw data does not carry phone numbers
    }


def _rocketreach_to_borealis(record: dict, b_id: str) -> dict:
    """Map a raw RocketReach record to the Borealis schema."""
    loc = record.get("location", {})
    city = loc.get("city", "") if isinstance(loc, dict) else ""
    state = loc.get("state", "") if isinstance(loc, dict) else ""
    country = loc.get("country", "") if isinstance(loc, dict) else ""
    full_location = ", ".join(filter(None, [city, state, country]))

    phones = record.get("phones", [])
    phone = phones[0] if phones else None

    socials = record.get("social_profiles", {})
    linkedin_url = socials.get("linkedin") if isinstance(socials, dict) else None
    if linkedin_url:
        linkedin_username = linkedin_url.strip().rstrip("/").split("/")[-1]
        linkedin = f"linkedin.com/in/{linkedin_username}"
    else:
        linkedin = None

    return {
        "source": "borealis",
        "b_id": b_id,
        "name": record.get("name"),
        "company": record.get("current_employer"),
        "position": record.get("current_title"),
        "linkedin": linkedin,
        "location": full_location or None,
        "phone": phone,
    }


# ---------------------------------------------------------------------------
# Static random profiles (for realism / padding)
# ---------------------------------------------------------------------------

_RANDOM_PROFILES = [
    {
        "source": "borealis",
        "b_id": "BOR_300",
        "name": "Alice Johnson",
        "company": "Tech Innovations Inc.",
        "position": "Software Engineer",
        "linkedin": "linkedin.com/in/alicej",
        "location": "San Francisco, CA, USA",
        "phone": "+1-555-0192",
    },
    {
        "source": "borealis",
        "b_id": "BOR_301",
        "name": "Bob Smith",
        "company": "Global Solutions Ltd.",
        "position": "Product Manager",
        "linkedin": "linkedin.com/in/bobsmith",
        "location": "London, UK",
        "phone": "+44-20-7123-4567",
    },
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    base_dir = Path(__file__).resolve().parent.parent
    data_lake = base_dir / "data-lake"

    # ------------------------------------------------------------------ #
    # Resolve latest date partitions for CoreSignal and RocketReach        #
    # ------------------------------------------------------------------ #
    cs_latest = get_latest_date_path(data_lake / "coresignal")
    rr_latest = get_latest_date_path(data_lake / "rocketreach")

    if cs_latest is None and rr_latest is None:
        print("[ERROR] No CoreSignal or RocketReach date partitions found in data-lake. Aborting.")
        return

    if cs_latest:
        print(f"CoreSignal  latest snapshot : {cs_latest}")
    else:
        print("[WARNING] No CoreSignal date partitions found – skipping CoreSignal records.")

    if rr_latest:
        print(f"RocketReach latest snapshot : {rr_latest}")
    else:
        print("[WARNING] No RocketReach date partitions found – skipping RocketReach records.")

    # ------------------------------------------------------------------ #
    # Build today's output path: data-lake/borealis/YYYY/MM/DD/           #
    # ------------------------------------------------------------------ #
    today = date.today()
    borealis_out_dir = (
        data_lake / "borealis"
        / f"{today.year:04d}"
        / f"{today.month:02d}"
        / f"{today.day:02d}"
    )
    borealis_out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Borealis output partition   : {borealis_out_dir}")

    # ------------------------------------------------------------------ #
    # Load raw records and convert to Borealis schema                      #
    # ------------------------------------------------------------------ #
    profiles: list[dict] = []

    # --- CoreSignal: take first 4 records ---
    if cs_latest:
        cs_records = _load_records(cs_latest)[:4]
        for i, record in enumerate(cs_records):
            profiles.append(_coresignal_to_borealis(record, b_id=f"BOR_{100 + i}"))
        print(f"  Added {len(cs_records)} CoreSignal profile(s).")

    # --- RocketReach: take first 4 records ---
    if rr_latest:
        rr_records = _load_records(rr_latest)[:4]
        for i, record in enumerate(rr_records):
            profiles.append(_rocketreach_to_borealis(record, b_id=f"BOR_{200 + i}"))
        print(f"  Added {len(rr_records)} RocketReach profile(s).")

    # --- Static random profiles ---
    profiles.extend(_RANDOM_PROFILES)

    # Shuffle for realism
    random.shuffle(profiles)

    # ------------------------------------------------------------------ #
    # Write output                                                         #
    # ------------------------------------------------------------------ #
    output_file = borealis_out_dir / "stakeholder.json"
    with open(output_file, "w", encoding="utf-8") as out_f:
        json.dump(profiles, out_f, indent=2)

    print(f"\nCreated {len(profiles)} profile(s) -> {output_file}")


if __name__ == "__main__":
    main()
