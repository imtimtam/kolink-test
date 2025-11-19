import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.get.env("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)


cur.execute("""
    CREATE TABLE IF NOT EXISTS pubmed (
        pmid BIGINT PRIMARY KEY,
        publication_type TEXT[],
        title TEXT NOT NULL,
        journal_title TEXT,
        authors JSONB,
        abstract TEXT,
        mesh_terms TEXT[],
        date_published DATE,
        lang TEXT
    );
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS clinicaltrials (
        nctid TEXT PRIMARY KEY,
        official_title TEXT,
        brief_title TEXT NOT NULL,
        brief_summary TEXT,
        org_name TEXT,
        lead_sponsor TEXT,
        collaborators TEXT[],
        conditions TEXT[],
        keywords TEXT[],
        phase TEXT[],
        status TEXT,
        start_date DATE,
        completion_date DATE,
        last_updated_date DATE
    )
""")
