from fastapi import APIRouter
from app.services.pubmed.api_pipeline import pubmed_services

router = APIRouter()

@router.get("/search/{term}")
def get_author_articles(term: str):
    pmids = pubmed_services.search(term)
    xml_data = pubmed_services.fetch_pubmed_metadata(pmids)
    parsed_data = pubmed_services.parse_pubmed_xml_to_json(xml_data)
    return parsed_data
