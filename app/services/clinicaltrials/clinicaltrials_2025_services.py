import json
from fastapi import FastAPI
import requests
import os

app = FastAPI()

CT_BASE_URL = "https://clinicaltrials.gov/api/v2/"
STUDIES_ENDPOINT = CT_BASE_URL + "/studies"
PAGE_SIZE = 1000

def clinicaltrials_fetch_batches(
        date_range: tuple[str, str] | None = None,
        pageSize: int = PAGE_SIZE,
        max_count: int | None = None,
):
    if date_range:
        start, end = date_range
    else:
        start, end = "2025-01-01", "2025-12-31" # default to 2025
    term = f"AREA[LastUpdatePostDate]RANGE[{start},{end}]"
    
    params = {
        "format": "json",
        "query.term": term,
        "fields": "ProtocolSection",
        "pageSize": pageSize,
    }

    page_token = None
    total_fetched = 0
    while True:
        if page_token:
            params["pageToken"] = page_token
        elif "pageToken" in params:
            del params["pageToken"]

        r = requests.get(STUDIES_ENDPOINT, params=params)
        r.raise_for_status()

        data = r.json()
        yield data

        if max_count is not None:
            total_fetched += len(data.get("studies", []))
            if total_fetched >= max_count:
                break

        page_token = data.get("nextPageToken")
        if not page_token: break

def parse_clinicaltrials_json(cts: dict):
    def clean_text(x):
        return x.strip() if x else None

    filtered = []
    for study in cts.get("studies", []):
        ps = study.get("protocolSection", {})

        id_mod = ps.get("identificationModule", {})
        org = id_mod.get("organization") or {}
        sponsor_collab_mod = ps.get("sponsorCollaboratorsModule", {})
        desc_mod = ps.get("descriptionModule", {})
        cond_mod = ps.get("conditionsModule", {})
        design_mod = ps.get("designModule", {})
        contact_loc_mod = ps.get("contactsLocationsModule", {})
        reference_mod = ps.get("referencesModule", {})
        status_mod = ps.get("statusModule", {})

        collaborators = [
            c.get("name")
            for c in sponsor_collab_mod.get("collaborators", [])
            if c.get("name")
        ]
        references = [
            ref.get("pmid")
            for ref in reference_mod.get("references", [])
            if ref.get("pmid")
        ]

        conditions = cond_mod.get("conditions") or []
        keywords = cond_mod.get("keywords") or []

        raw_phases = design_mod.get("phases") or []
        phases = raw_phases if raw_phases not in [[], ["NA"]] else []

        locations = contact_loc_mod.get("locations") or []
        first_loc = locations[0] if locations else {}

        filtered.append({
            "nct_id": clean_text(id_mod.get("nctId")),
            "official_title": clean_text(id_mod.get("officialTitle")),
            "brief_title": clean_text(id_mod.get("briefTitle")),
            "org_name": clean_text(org.get("fullName")),
            "lead_sponsor": clean_text(sponsor_collab_mod.get("leadSponsor", {}).get("name")),
            "collaborators": collaborators,
            "brief_summary": clean_text(desc_mod.get("briefSummary")),
            "conditions": conditions,
            "keywords": keywords,
            "study_type": clean_text(design_mod.get("studyType")),
            "phase": phases,
            "city": clean_text(first_loc.get("city")),
            "state": clean_text(first_loc.get("state")),
            "zip": clean_text(first_loc.get("zip")),
            "country": clean_text(first_loc.get("country")),
            "status": clean_text(status_mod.get("overallStatus")),
            "reference_pmid": references,
            "start_date": parse_date(status_mod.get("startDateStruct", {}).get("date")),
            "completion_date": parse_date(status_mod.get("completionDateStruct", {}).get("date")),
            "last_update_post_date": parse_date(status_mod.get("lastUpdatePostDateStruct", {}).get("date"))
        })
    return filtered

def parse_date(date_str: str):
    if not date_str: return None
    split = date_str.split("-")
    year = split[0]
    month = split[1].zfill(2) if len(split) > 1 else "01"
    day = split[2].zfill(2) if len(split) > 2  else "01"
    return f"{year}-{month}-{day}"

def export_year(year: int):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_FOLDER = os.path.join(script_dir, "..", "exports")
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    OUTPUT_FILE = f"clinicaltrials_{year}.jsonl"
    full_path = os.path.join(OUTPUT_FOLDER, OUTPUT_FILE)

    start, end = f"{year}-01-01", f"{year}-12-31"
    all_trials = []
    for batch in clinicaltrials_fetch_batches(date_range=(start, end)):
        parsed_trials = parse_clinicaltrials_json(batch)
        all_trials.extend(parsed_trials)
        print(f"Processed {len(parsed_trials)} trials (Total so far: {len(all_trials)})")

    with open(full_path, "w", encoding="utf-8") as f:
        for trial in all_trials:
            f.write(json.dumps(trial, ensure_ascii=False) + "\n")

    print(f"All trials for {year} exported to {full_path}")

if __name__ == "__main__":
    # for year in range(2021, 2026):
    #     export_year(year)
    for batch in clinicaltrials_fetch_batches(max_count=20, pageSize=5):
        parsed_trials = parse_clinicaltrials_json(batch)
        print(json.dumps(parsed_trials, indent=2))