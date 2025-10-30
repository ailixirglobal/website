import csv
import re
from pathlib import Path

# Path to your herbal dataset (update as needed)
HERBAL_DATASET_PATH = Path("datasets/ailixir_herbal_dataset_10000.csv")

# Cache the dataset in memory
herbal_database = []


def load_herbal_database():
    """Loads herbal dataset from CSV using only Python's csv module."""
    global herbal_database

    if herbal_database:  # already loaded
        return herbal_database

    herbs = []
    if HERBAL_DATASET_PATH.exists():
        with open(HERBAL_DATASET_PATH, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                herbs.append({
                    "name": row.get("Common Name") or row.get("Herb Name") or "Unknown Herb",
                    #"local_name": row.get("Local Name (Hausa)") or row.get("Local Name") or "N/A",
                    "scientific_name": row.get("Botanical Name") or "N/A",
                    #"type": row.get("Type") or row.get("Category") or "General Herb",
                    "description": row.get("Health Conditions Treated") or "",
                    "uses": row.get("Common Uses") or "",
                    #"reason": row.get("Notes") or row.get("Recommendation") or "",
                })
    else:
        print("⚠️ Dataset not found at:", HERBAL_DATASET_PATH)

    herbal_database = herbs
    print(f"🌿 Loaded {len(herbs)} herbs into memory.")
    return herbs


def analyze_herbal_symptoms(symptoms_text: str, limit: int = 5):
    """Analyzes user symptoms dynamically and returns top herbs."""
    if not symptoms_text.strip():
        return []

    herbs = load_herbal_database()
    symptoms = symptoms_text.lower()
    keywords = re.findall(r'\b[a-z]+\b', symptoms)
    results = []

    for herb in herbs:
        
        # Create searchable text blob
        searchable_text = " ".join([
            herb["name"], herb["description"],
            herb["uses"]
        ]).lower()

        # Score the herb by keyword match
        score = sum(1 for kw in keywords if kw in searchable_text)

        if score > 0:
            results.append({**herb, "score": score})

    # Sort and limit results
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]