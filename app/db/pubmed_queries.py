from db.connection import get_connection

conn = get_connection()
cur = conn.cursor()

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

def upsert_pubmed(article):
    pass