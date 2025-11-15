from dotenv import load_dotenv
from supabase import create_client, Client
import os

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def cache_pubmed_entries(entries: list[dict]):
    if not entries:
        return None
    return supabase.table("pubmed").upsert(entries, on_conflict="pmid").execute()

def cache_clinicaltrials_entries(entries: list[dict]):
    if not entries:
        return None
    return supabase.table("clinicaltrials").upsert(entries, on_conflict="nct_id").execute()