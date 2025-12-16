from dotenv import load_dotenv
from supabase import create_client, Client
from pathlib import Path
import os
import json
import csv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

pubmed_folder: Path = Path(os.environ.get("OUTPUT_DIR"))
clinicaltrials_folder: Path = Path(os.environ.get("OUTPUT_CT_DIR"))
cms_folder: Path = Path(os.environ.get("OUTPUT_CMS_DIR"))

def cache_pubmed_entries(start_year: int, end_year: int):
    for year in range(start_year, end_year + 1):
        year_folder = pubmed_folder / str(year)
        for file in year_folder.iterdir():
            if not file.is_file():
                continue
            
            entries = []
            with file.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line: continue

                    data = json.loads(line)

                    # must have primary key
                    pubmed_id = data.get("pmid")
                    if not pubmed_id: continue
                    date_published = data.get("date_published")
                    entry = {
                        "pubmed_id": pubmed_id,
                        "title": data.get("title"),
                        "journal": data.get("journal_title"),
                        "publication_type": join_list(data.get("publication_types", [])),
                        "year": int(date_published[:4]) if date_published else None
                    }
                    entries.append(entry)
                    if len(entries) >= 500:
                        print("Upserting 500 entries")
                        # solves upsert error where duplicates may exist due to updating publications
                        unique_entries = {e["pubmed_id"]: e for e in entries}
                        supabase.table("publications").upsert(list(unique_entries.values()), on_conflict="pubmed_id").execute()
                        entries.clear()
            
            if entries:
                print("Upserting final batch")
                unique_entries = {e["pubmed_id"]: e for e in entries}
                supabase.table("publications").upsert(list(unique_entries.values()), on_conflict="pubmed_id").execute()

def cache_clinicaltrials_entries(start_year: int, end_year: int):
    for year in range(start_year, end_year + 1):
        for file in clinicaltrials_folder.glob(f"*{year}.jsonl"):
            if not file.is_file():
                continue

            entries = []
            with file.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line: continue

                    data = json.loads(line)

                    # must have primary key
                    trial_id = data.get("nct_id")
                    if not trial_id: continue
                    start_date = data.get("start_date")
                    entry = {
                        "trial_id": trial_id,
                        "title": data.get("brief_title"),
                        "conditions": join_list(data.get("conditions", [])),
                        "phase": join_list(data.get("phase", [])),
                        "status": data.get("status"),
                        "start_year": int(start_date[:4]) if start_date else None
                    }
                    entries.append(entry)

                    if len(entries) >= 500:
                        print("Upserting 500 entries")
                        supabase.table("clinicaltrials").upsert(entries, on_conflict="trial_id").execute()
                        entries.clear()
            
            if entries:
                print("Upserting final batch")
                supabase.table("clinicaltrials").upsert(entries, on_conflict="trial_id").execute()

def cache_cms_payment_entries(start_year: int, end_year: int):
    for year in range(start_year, end_year + 1):
        for file in cms_folder.glob(f"*{year}.csv"):
            if not file.is_file():
                continue

            entries = []
            with file.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for data in reader:
                    # must have primary key
                    record_id = data.get("record_id")
                    if not record_id: continue
                    year = data.get("program_year")
                    entry = {
                        "record_id": record_id,
                        "recipient_npi": data.get("covered_recipient_npi"),
                        "amount": float(data.get("total_amount_of_payment_usdollars")),
                        "payer": data.get("applicable_manufacturer_or_applicable_gpo_making_payment_name"),
                        "transaction_type": data.get("transaction_type"),
                        "year": int(year) if year else None
                    }
                    entries.append(entry)
                    if len(entries) >= 500:
                        print("Upserting 500 entries")
                        supabase.table("payments").upsert(entries, on_conflict="record_id").execute()
                        entries.clear()
            
            if entries:
                print("Upserting final batch")
                supabase.table("payments").upsert(entries, on_conflict="record_id").execute()

def join_list(list: list[str]):
    return ", ".join(list) if list else None

if __name__ == "__main__":
    #cache_pubmed_entries(2024, 2024)
    #cache_clinicaltrials_entries(2024, 2024)
    cache_cms_payment_entries(2024, 2024)




