from pydantic import BaseModel
from datetime import date

class ClinicalTrialsSearchResponse(BaseModel):
    nct_id: str
    official_title: str | None
    brief_title: str
    org_name: str | None
    lead_sponsor: str | None
    collaborators: list[str] | None
    brief_summary: str | None
    conditions: list[str] | None
    keywords: list[str] | None
    study_type: str | None
    phase: list[str] | None
    city: str | None
    state: str | None
    zip: str | None
    country: str | None
    status: str | None
    reference_pmid: list[str] | None
    start_date: date | None
    completion_date: date | None
    last_update_post_date: date | None

    model_config = {
        "from_attributes": True
    }