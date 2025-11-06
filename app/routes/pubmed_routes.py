from fastapi import APIRouter
from app.services import pubmed_services

router = APIRouter()

@router.get("/author/{author_name}")
def get_author_articles(author_name: str):
    pmids = pubmed_services.get_author_pmids(author_name)
    xml_data = pubmed_services.fetch_pubmed_metadata(pmids)
    parsed_data = pubmed_services.parse_pubmed_xml_to_json(xml_data)
    return parsed_data
