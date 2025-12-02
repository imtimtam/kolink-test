from pydantic import BaseModel
from datetime import date

class Author(BaseModel):
    full_name: str | None
    affiliations: list[str] | None

class PubMedSearchResponse(BaseModel):
    pmid: int
    publication_types: list[str]
    title: str | None
    journal_title: str | None
    authors: list[Author]
    abstract: str | None
    mesh_terms: list[str]
    date_published: date | None
    language: str | None

    model_config = {
        "from_attributes": True
    }