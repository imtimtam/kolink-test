import json
import os
from dotenv import load_dotenv
from app.db.models import ClinicalTrials
from app.db.session import SessionLocal
from app.utils.date_utils import str_to_date

load_dotenv()
FOLDER_PATH = os.getenv("OUTPUT_CT_DIR")

def load_clinicaltrials_jsonl(file_path: str):
    with SessionLocal() as db:
        
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)

                nct_id = record.get("nct_id")
                brief_title = record.get("brief_title")
                if not nct_id or not brief_title: # primary key check
                    continue

                clinicaltrials_entry = ClinicalTrials(
                    nct_id = nct_id,
                    official_title = record.get("official_title"),
                    brief_title = brief_title,
                    org_name = record.get("org_name"),
                    lead_sponsor = record.get("lead_sponsor"),
                    collaborators = record.get("collaborators"),
                    brief_summary = record.get("brief_summary"),
                    conditions = record.get("conditions"),
                    keywords = record.get("keywords"),
                    study_type = record.get("study_type"),
                    phase = record.get("phase"),
                    city = record.get("city"),
                    state = record.get("state"),
                    zip = record.get("zip"),
                    country = record.get("country"),
                    status = record.get("status"),
                    reference_pmid = record.get("reference_pmid"),
                    start_date = str_to_date(record.get("start_date")),
                    completion_date = str_to_date(record.get("completion_date")),
                    last_update_post_date = str_to_date(record.get("last_update_post_date"))               
                )
                db.merge(clinicaltrials_entry)  # Merge equivalent to insert/update
        db.commit()

if __name__ == "__main__":
    #python -m app.services.clinicaltrials.clinicaltrials_loader
    file_path = os.path.join(FOLDER_PATH, "clinicaltrials_2025.jsonl")
    load_clinicaltrials_jsonl(file_path)