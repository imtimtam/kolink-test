import json
from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

CT_BASE_URL = "https://clinicaltrials.gov/api/v2/"
STUDIES_ENDPOINT = CT_BASE_URL + "/studies"

STATUS_GROUPS = {
    "active": ["ACTIVE_NOT_RECRUITING", "ENROLLING_BY_INVITATION", "NOT_YET_RECRUITING", "RECRUITING"],
    "completed": ["COMPLETED", "APPROVED_FOR_MARKETING", "AVAILABLE"],
    "paused": ["SUSPENDED", "TEMPORARILY_NOT_AVAILABLE"],
    "terminated": ["TERMINATED", "WITHDRAWN", "NO_LONGER_AVAILABLE", "WITHHELD"]
}

def get_cts(term: str | None = None, status: str | list[str]= "completed"):
    term = term or ""

    if isinstance(status, str):
        status = [status]
    overall_status = []
    for s in status:
        s_lower = s.lower()
        if s_lower in STATUS_GROUPS:
            overall_status.extend(STATUS_GROUPS.get(s_lower, []))
        else:
            overall_status.append(s.upper())

    params = {
        "format": "json",
        "query.term": term,
        "filter.overallStatus": ",".join(overall_status),
        "fields": "ProtocolSection",
        "pageSize": 3
    }
    r = requests.get(STUDIES_ENDPOINT, params=params)
    r.raise_for_status()
    data = r.json()

    filtered = []
    for study in data.get("studies", []):
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
            "status": status_mod.get("overallStatus", []),
            "start_date": status_mod.get("startDateStruct", {}).get("date", ""),
            "completion_date": status_mod.get("completionDateStruct", {}).get("date", ""),
        })
    return filtered

if __name__ == "__main__":
    r = get_cts(term="diabetes", status=["completed"])
    print(json.dumps(r, indent=2))
    #print(get_cts_on_condition("diabetes"))