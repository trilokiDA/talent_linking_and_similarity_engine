"""
Generate synthetic stakeholder profiles for ATLAS PoC
Creates realistic dummy data for CoreSignal and RocketReach APIs
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Seed for reproducibility
random.seed(42)

# Reference data for generating realistic profiles
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Barbara", "David", "Elizabeth", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Wei", "Yuki", "Raj", "Priya", "Mohammed", "Fatima", "Chen", "Mei",
    "Carlos", "Maria", "Ahmed", "Aisha", "Pierre", "Sophie", "Hans", "Anna"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White", "Harris",
    "Chen", "Wang", "Zhang", "Liu", "Kumar", "Patel", "Singh", "Khan",
    "Kim", "Park", "Tanaka", "Sato", "Schmidt", "Mueller", "Dubois", "Bernard",
    "O'Brien", "Murphy", "Kelly", "Ryan", "Cohen", "Levy", "Ahmed", "Hassan"
]

TITLES = [
    "Professor", "Associate Professor", "Assistant Professor", "Research Scientist",
    "Senior Research Scientist", "Principal Investigator", "Research Fellow", "Postdoctoral Researcher",
    "Lab Director", "Department Chair", "Research Director", "Lead Scientist",
    "Senior Scientist", "Staff Scientist", "Group Leader", "Research Associate Professor",
    "Emeritus Professor", "Visiting Professor", "Adjunct Professor", "Clinical Professor"
]

INSTITUTIONS = [
    "Stanford University", "MIT", "Harvard University", "University of California Berkeley",
    "Oxford University", "Cambridge University", "ETH Zurich", "Max Planck Institute",
    "Yale University", "Princeton University", "Columbia University", "University of Chicago",
    "Johns Hopkins University", "University of Pennsylvania", "Duke University", "Northwestern University",
    "Caltech", "University of Michigan", "Cornell University", "UCLA",
    "University of Toronto", "McGill University", "Imperial College London", "University College London",
    "Technical University of Munich", "Karolinska Institute", "National University of Singapore", "Tsinghua University",
    "Peking University", "Tokyo University", "Kyoto University", "Australian National University"
]

DEPARTMENTS = [
    "Neuroscience", "Molecular Biology", "Chemistry", "Physics", "Computer Science",
    "Bioengineering", "Genetics", "Immunology", "Pharmacology", "Biochemistry",
    "Materials Science", "Applied Mathematics", "Electrical Engineering", "Mechanical Engineering",
    "Computational Biology", "Biophysics", "Cell Biology", "Microbiology", "Cancer Research",
    "Data Science", "Artificial Intelligence", "Quantum Computing", "Nanotechnology", "Environmental Science"
]

RESEARCH_AREAS = [
    "Cancer immunotherapy", "CRISPR gene editing", "Neural networks", "Quantum mechanics",
    "Drug discovery", "Stem cell research", "Climate modeling", "Machine learning",
    "Protein folding", "Vaccine development", "Renewable energy", "Artificial intelligence",
    "Genomics", "Neurodegenerative diseases", "Synthetic biology", "Materials engineering",
    "Computational chemistry", "Brain-computer interfaces", "Precision medicine", "Nanotechnology"
]

JOURNALS = [
    "Nature", "Science", "Cell", "The Lancet", "NEJM", "PNAS", "Nature Medicine",
    "Nature Biotechnology", "Nature Neuroscience", "Nature Genetics", "Cell Stem Cell",
    "Immunity", "Cancer Cell", "Neuron", "Molecular Cell", "Cell Reports", "eLife",
    "PLOS Biology", "Nature Communications", "Scientific Reports", "Genome Research"
]

CITIES = [
    "Boston, MA", "Cambridge, MA", "Palo Alto, CA", "Berkeley, CA", "New York, NY",
    "Chicago, IL", "San Francisco, CA", "Los Angeles, CA", "San Diego, CA", "Seattle, WA",
    "London, UK", "Oxford, UK", "Cambridge, UK", "Zurich, Switzerland", "Munich, Germany",
    "Berlin, Germany", "Paris, France", "Toronto, Canada", "Singapore", "Tokyo, Japan",
    "Beijing, China", "Shanghai, China", "Sydney, Australia", "Melbourne, Australia"
]


def generate_email(first_name, last_name, institution):
    """Generate realistic academic email"""
    domains = {
        "Stanford University": "stanford.edu",
        "MIT": "mit.edu",
        "Harvard University": "harvard.edu",
        "University of California Berkeley": "berkeley.edu",
        "Oxford University": "ox.ac.uk",
        "Cambridge University": "cam.ac.uk",
        "Yale University": "yale.edu",
        "Princeton University": "princeton.edu"
    }

    domain = domains.get(institution, institution.lower().replace(" ", "").replace("university", "u") + ".edu")

    formats = [
        f"{first_name[0].lower()}.{last_name.lower()}@{domain}",
        f"{first_name.lower()}.{last_name.lower()}@{domain}",
        f"{first_name.lower()}{last_name[0].lower()}@{domain}",
        f"{last_name.lower()}@{domain}"
    ]

    return random.choice(formats)


def generate_orcid():
    """Generate realistic ORCID ID"""
    parts = [f"{random.randint(0, 9999):04d}" for _ in range(4)]
    return f"0000-{parts[0]}-{parts[1]}-{parts[2]}"


def generate_publications(name):
    """Generate publication records"""
    num_pubs = random.randint(5, 30)
    publications = []

    for i in range(num_pubs):
        year = random.randint(2015, 2026)
        journal = random.choice(JOURNALS)
        citations = random.randint(0, 500)

        publications.append({
            "title": f"Research study {i+1} on {random.choice(RESEARCH_AREAS).lower()}",
            "journal": journal,
            "year": year,
            "citations": citations,
            "authors": f"{name} et al."
        })

    return sorted(publications, key=lambda x: x['year'], reverse=True)


def generate_coresignal_profile(profile_id):
    """Generate CoreSignal-style profile"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    full_name = f"Dr. {first_name} {last_name}"

    institution = random.choice(INSTITUTIONS)
    title = random.choice(TITLES)
    department = random.choice(DEPARTMENTS)

    # Education history
    education = [
        {
            "institution": random.choice([i for i in INSTITUTIONS if i != institution]),
            "degree": "PhD",
            "field": department,
            "start_year": random.randint(2000, 2010),
            "end_year": random.randint(2010, 2015)
        },
        {
            "institution": random.choice(INSTITUTIONS),
            "degree": "BS/MS",
            "field": department,
            "start_year": random.randint(1995, 2005),
            "end_year": random.randint(2005, 2010)
        }
    ]

    # Work experience
    years_at_current = random.randint(1, 15)
    experience = [
        {
            "company": institution,
            "position": title,
            "department": f"Department of {department}",
            "start_date": (datetime.now() - timedelta(days=365*years_at_current)).strftime("%Y-%m-%d"),
            "end_date": None,
            "is_current": True
        }
    ]

    # Add previous positions for senior researchers
    if "Professor" in title or "Director" in title:
        prev_institution = random.choice([i for i in INSTITUTIONS if i != institution])
        experience.append({
            "company": prev_institution,
            "position": "Assistant Professor" if "Professor" in title else "Senior Scientist",
            "department": f"Department of {department}",
            "start_date": (datetime.now() - timedelta(days=365*(years_at_current+8))).strftime("%Y-%m-%d"),
            "end_date": (datetime.now() - timedelta(days=365*years_at_current)).strftime("%Y-%m-%d"),
            "is_current": False
        })

    profile = {
        "source": "coresignal",
        "person_id": f"CS_{profile_id:06d}",
        "full_name": full_name,
        "first_name": first_name,
        "last_name": last_name,
        "title": title,
        "current_company": institution,
        "department": department,
        "location": random.choice(CITIES),
        "country": random.choice(["USA", "UK", "Switzerland", "Germany", "Canada", "Singapore", "China", "Japan", "Australia"]),
        "education": education,
        "experience": experience,
        "skills": random.sample(RESEARCH_AREAS, k=random.randint(3, 6)),
        "research_interests": random.sample(RESEARCH_AREAS, k=random.randint(2, 4)),
        "linkedin_url": f"linkedin.com/in/{first_name.lower()}{last_name.lower()}{random.randint(100,999)}",
        "h_index": random.randint(10, 80),
        "total_citations": random.randint(500, 10000),
        "total_publications": random.randint(15, 150),
        "data_quality_score": round(random.uniform(0.7, 1.0), 2),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "profile_completeness": random.randint(75, 100)
    }

    return profile


def generate_rocketreach_profile(profile_id):
    """Generate RocketReach-style profile"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    full_name = f"Dr. {first_name} {last_name}"

    institution = random.choice(INSTITUTIONS)
    title = random.choice(TITLES)
    department = random.choice(DEPARTMENTS)

    email = generate_email(first_name, last_name, institution)
    orcid = generate_orcid()

    # Phone number
    phone_formats = [
        f"+1-{random.randint(200,999)}-{random.randint(200,999)}-{random.randint(1000,9999)}",
        f"+44-{random.randint(20,99)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
        f"+49-{random.randint(20,99)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
    ]

    publications = generate_publications(full_name)

    profile = {
        "source": "rocketreach",
        "id": f"RR_{profile_id:06d}",
        "name": full_name,
        "first_name": first_name,
        "last_name": last_name,
        "current_employer": institution,
        "current_title": title,
        "department": f"Department of {department}",
        "emails": [
            email,
            f"{first_name.lower()}.{last_name.lower()}@gmail.com"
        ],
        "phones": [random.choice(phone_formats)],
        "location": {
            "city": random.choice(CITIES).split(",")[0],
            "state": random.choice(CITIES).split(",")[-1].strip() if "," in random.choice(CITIES) else None,
            "country": random.choice(["USA", "UK", "Switzerland", "Germany", "Canada"])
        },
        "social_profiles": {
            "linkedin": f"https://linkedin.com/in/{first_name.lower()}{last_name.lower()}",
            "twitter": f"https://twitter.com/{first_name.lower()}{last_name[0].lower()}_research" if random.random() > 0.3 else None,
            "google_scholar": f"https://scholar.google.com/citations?user={random.randint(1000000,9999999)}",
            "orcid": f"https://orcid.org/{orcid}",
            "researchgate": f"https://researchgate.net/profile/{first_name}_{last_name}"
        },
        "publications": publications[:10],  # Top 10 recent publications
        "total_publications": len(publications),
        "h_index": random.randint(10, 80),
        "i10_index": random.randint(5, 60),
        "total_citations": sum(p['citations'] for p in publications),
        "research_areas": random.sample(RESEARCH_AREAS, k=random.randint(2, 5)),
        "orcid_id": orcid,
        "verified_email": random.choice([True, True, True, False]),  # 75% verified
        "profile_url": f"https://rocketreach.co/person/{first_name.lower()}-{last_name.lower()}-{profile_id}",
        "confidence_score": round(random.uniform(0.75, 0.99), 2),
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "data_freshness_days": random.randint(1, 30)
    }

    return profile


def generate_stakeholder_data(source_type, num_profiles=100):
    """Generate stakeholder profiles for a given source"""
    profiles = []

    for i in range(1, num_profiles + 1):
        if source_type == "coresignal":
            profile = generate_coresignal_profile(i)
        else:  # rocketreach
            profile = generate_rocketreach_profile(i)

        profiles.append(profile)

    return profiles


def main():
    """Generate and save dummy data"""
    today = datetime.now()
    year = today.year
    month = f"{today.month:02d}"
    day = f"{today.day:02d}"

    base_path = Path("data-lake")

    # Generate CoreSignal data
    print("Generating CoreSignal profiles...")
    coresignal_profiles = generate_stakeholder_data("coresignal", 100)
    coresignal_path = base_path / "coresignal" / str(year) / month / day
    coresignal_path.mkdir(parents=True, exist_ok=True)

    with open(coresignal_path / "stakeholder.json", "w") as f:
        json.dump(coresignal_profiles, f, indent=2)

    print(f"[OK] Created {len(coresignal_profiles)} CoreSignal profiles at {coresignal_path}/stakeholder.json")

    # Generate RocketReach data
    print("\nGenerating RocketReach profiles...")
    rocketreach_profiles = generate_stakeholder_data("rocketreach", 100)
    rocketreach_path = base_path / "rocketreach" / str(year) / month / day
    rocketreach_path.mkdir(parents=True, exist_ok=True)

    with open(rocketreach_path / "stakeholder.json", "w") as f:
        json.dump(rocketreach_profiles, f, indent=2)

    print(f"[OK] Created {len(rocketreach_profiles)} RocketReach profiles at {rocketreach_path}/stakeholder.json")

    # Summary statistics
    print("\n" + "="*60)
    print("DATA GENERATION SUMMARY")
    print("="*60)
    print(f"Date: {year}-{month}-{day}")
    print(f"CoreSignal profiles: {len(coresignal_profiles)}")
    print(f"RocketReach profiles: {len(rocketreach_profiles)}")
    print(f"Total profiles: {len(coresignal_profiles) + len(rocketreach_profiles)}")

    # Sample profile preview
    print("\n" + "="*60)
    print("SAMPLE CORESIGNAL PROFILE")
    print("="*60)
    print(json.dumps(coresignal_profiles[0], indent=2))

    print("\n" + "="*60)
    print("SAMPLE ROCKETREACH PROFILE")
    print("="*60)
    print(json.dumps(rocketreach_profiles[0], indent=2))


if __name__ == "__main__":
    main()
