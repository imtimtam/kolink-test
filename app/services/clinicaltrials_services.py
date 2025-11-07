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
        "pageSize": 1
    }
    r = requests.get(STUDIES_ENDPOINT, params=params)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    print(get_cts(term="diabetes", status=["paused", "terminated"]))
    #print(get_cts_on_condition("diabetes"))