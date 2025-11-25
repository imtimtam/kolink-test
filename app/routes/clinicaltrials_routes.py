from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, select, or_
from datetime import date
from typing import List

from app.routes.clinicaltrials_models import ClinicalTrialsSearchResponse
from app.db.session import get_db
from app.db.models import ClinicalTrials

# uvicorn app.routes.clinicaltrials_routes:app --reload
router = APIRouter()

@router.get("/clinicaltrials", response_model=List[ClinicalTrialsSearchResponse])
def search_clinicaltrials(
    term: str | None = None,
    nct_id: str | None = None,
    org_name: str | None = None,
    lead_sponsor: str | None = None,
    conditions: str | None = None,
    study_type: str | None = None,
    phase: str | None = None,
    status: str | None = None,
    start_date: date | None = None,
    completion_date: date | None = None,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    stmt = select(ClinicalTrials)
    filters = []

    if nct_id:
        filters.append(ClinicalTrials.nct_id == nct_id)
    if org_name:
        filters.append(ClinicalTrials.org_name.ilike(f"%{org_name}%"))
    if lead_sponsor:
        filters.append(ClinicalTrials.lead_sponsor.ilike(f"%{lead_sponsor}%"))
    if conditions:
        filters.append(func.array_to_string(ClinicalTrials.conditions, '||').ilike(f"%{conditions}%"))
    if study_type:
        filters.append(ClinicalTrials.study_type.ilike(f"%{study_type}%"))
    if phase:
        filters.append(func.array_to_string(ClinicalTrials.phase, '||').ilike(f"%{phase}%"))
    if status:
        filters.append(ClinicalTrials.status.ilike(f"%{status}%"))
    if start_date:
        filters.append(ClinicalTrials.start_date >= start_date)
    if completion_date:
        filters.append(ClinicalTrials.completion_date <= completion_date)
    
    if term:
        filters.append(or_(
            ClinicalTrials.official_title.ilike(f"%{term}%"),
            ClinicalTrials.brief_title.ilike(f"%{term}%"),
            ClinicalTrials.brief_summary.ilike(f"%{term}%"),
            func.array_to_string(ClinicalTrials.conditions, "||").ilike(f"%{term}%"),
            func.array_to_string(ClinicalTrials.keywords, "||").ilike(f"%{term}%"),
        ))

    if filters:
        stmt = stmt.where(*filters)
    if limit:
        stmt = stmt.limit(limit)

    results = db.scalars(stmt).all()
    if not results:
        raise HTTPException(status_code=404, detail="No matching Clinical Trials found.")
    return [ClinicalTrialsSearchResponse.model_validate(result) for result in results]

@router.get("/clinicaltrials/{nct_id}", response_model=ClinicalTrialsSearchResponse)
def profile_clinicaltrials_nct_id(
    nct_id: str,
    db: Session = Depends(get_db)
):
    stmt = select(ClinicalTrials).where(ClinicalTrials.nct_id == nct_id)
    results = db.scalars(stmt).first()
    if not results:
        raise HTTPException(status_code=404, detail="No matching Clinical Trials found.")
    return ClinicalTrialsSearchResponse.model_validate(results)