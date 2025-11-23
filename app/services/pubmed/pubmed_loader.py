import json
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.db.models import PubMed
from app.db.session import Session
from app.utils.date_utils import str_to_date

load_dotenv()
FOLDER_PATH = os.getenv("OUTPUT_DIR")

def load_pubmed_jsonl(file_path: str):
    db = Session()

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)

            pmid = record.get("pmid")
            title = record.get("title")
            if not pmid or not title: # primary key check
                continue

            pubmed_entry = PubMed(
                pmid = int(pmid),
                publication_types = record.get("publication_types"),
                title = record.get("title"),
                journal_title = record.get("journal_title"),
                authors = record.get("authors"),
                abstract = record.get("abstract"),
                mesh_terms = record.get("mesh_terms"),
                date_published = str_to_date(record.get("date_published")),
                lang = record.get("lang")
            )
            db.merge(pubmed_entry)  # Merge equivalent to insert/update
    db.commit()
    db.close()

if __name__ == "__main__":
    #python -m app.services.pubmed.pubmed_loader
    file_path = os.path.join(FOLDER_PATH, "2025", "pubmed25n1637.jsonl")
    load_pubmed_jsonl(file_path)