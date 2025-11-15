import json
from cache_services import cache_clinicaltrials_entries
from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

CT_BASE_URL = "https://clinicaltrials.gov/api/v2/"
STUDIES_ENDPOINT = CT_BASE_URL + "/studies"

def clinicaltrials_fetch_batches(
        term: str | None = None,
        last_update_range: tuple[str, str] | None = None,
        pageSize: int = 5,
        max_count: int | None = None,
):
    term = term.strip() or ""
    if last_update_range:
        start, end = last_update_range
    else:
        start, end = "2025-01-01", "2025-12-31"
    term += f" AND AREA[LastUpdatePostDate]RANGE[{start},{end}]"
    
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
    filtered = []
    for study in cts.get("studies", []):
        ps = study.get("protocolSection", {})
        rs = study.get("resultsSection", {})

        id_mod = ps.get("identificationModule", {})
        sponsor_collaborators = ps.get("sponsorCollaboratorsModule", {})
        desc_mod = ps.get("descriptionModule", {})
        cond_mod = ps.get("conditionsModule", {})
        design_mod = ps.get("designModule", {})
        outcome_mod = ps.get("outcomesModule", {})
        eligibility_mod = ps.get("eligibilityModule", {})
        contact_loc_mod = ps.get("contactsLocationsModule", {})
        reference_mod = ps.get("referencesModule", {})
        status_mod = ps.get("statusModule", {})

        filtered.append({
            "nct_id": id_mod.get("nctId", ""),
            "official_title": id_mod.get("officialTitle", ""),
            "brief_title": id_mod.get("briefTitle", ""),
            "org_name": id_mod.get("organization", "").get("fullName", ""),
            "lead_sponsor": sponsor_collaborators.get("leadSponsor", {}).get("name", ""),
            "collaborators": [c.get("name", "") for c in sponsor_collaborators.get("collaborators", []) if c.get("name")],
            "brief_summary": desc_mod.get("briefSummary", ""),
            "conditions": cond_mod.get("conditions", []),
            "keywords": cond_mod.get("keywords", []),
            #"study_type": design_mod.get("studyType", ""),
            #"enroll_count": design_mod.get("enrollmentInfo", {}).get("count", None),
            #"outcome": outcome_mod,
            #"eligibility": eligibility_mod,
            #"contact_loc": contact_loc_mod,
            "references": reference_mod, #?
            #"res": rs.get("outcomeMeasuresModule", {}), #?
            "phase": design_mod.get("phases", []),
            "status": status_mod.get("overallStatus", ""),
            "start_date": parse_date(status_mod.get("startDateStruct", {}).get("date", "")),
            "completion_date": parse_date(status_mod.get("completionDateStruct", {}).get("date", "")),
            "last_update_post_date": parse_date(status_mod.get("lastUpdatePostDateStruct", {}).get("date", ""))
        })
    return filtered

def parse_date(date_str: str):
    if not date_str: return None
    split = date_str.split("-")
    year = split[0]
    month = split[1].zfill(2) if len(split) > 1 else "01"
    day = split[2].zfill(2) if len(split) > 2  else "01"
    return f"{year}-{month}-{day}"

if __name__ == "__main__":
    for batch in clinicaltrials_fetch_batches(term="covid-19", max_count=20, pageSize=5):
        parsed_trials = parse_clinicaltrials_json(batch)
        print(json.dumps(parsed_trials, indent=2))