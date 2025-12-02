from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, select, or_
from datetime import date
from typing import List

from app.routes.pubmed_models import PubMedSearchResponse
from app.db.session import get_db
from app.db.models import PubMed

# uvicorn app.routes.pubmed_routes:app --reload
router = APIRouter()

@router.get("/pubmed", response_model=List[PubMedSearchResponse])
def search_pubmed(
    term: str | None = None,
    pmid: int | None = None,
    publication_type: str | None = None,
    author: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    language: str | None = None,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    stmt = select(PubMed)
    filters = []

    if pmid:
        filters.append(PubMed.pmid == pmid)
    if publication_type:
        filters.append(func.array_to_string(PubMed.publication_types, '||').ilike(f"%{publication_type}%"))
    if author:
        filters.append(PubMed.authors.ilike(f"%{author}%"))
    if start_date:
        filters.append(PubMed.date_published >= start_date)
    if end_date:
        filters.append(PubMed.date_published <= end_date)
    if language:
        filters.append(PubMed.language.ilike(f"%{language}%"))
    
    if term:
        filters.append(or_(
            PubMed.title.ilike(f"%{term}%"),
            PubMed.journal_title.ilike(f"%{term}%"),
            PubMed.abstract.ilike(f"%{term}%"),
            func.array_to_string(PubMed.mesh_terms, '||').ilike(f"%{term}%")
        ))

    if filters:
        stmt = stmt.where(*filters)
    if limit:
        stmt = stmt.limit(limit)

    results = db.scalars(stmt).all()
    if not results:
        raise HTTPException(status_code=404, detail="No matching PubMed articles found.")
    return [PubMedSearchResponse.model_validate(result) for result in results]

@router.get("/pubmed/{pmid}", response_model=PubMedSearchResponse)
def profile_pubmed_pmid(
    pmid: int,
    db: Session = Depends(get_db)
):
    stmt = select(PubMed).where(PubMed.pmid == pmid)
    results = db.scalars(stmt).first()
    if not results:
        raise HTTPException(status_code=404, detail="No matching PubMed articles found.")
    return PubMedSearchResponse.model_validate(results)