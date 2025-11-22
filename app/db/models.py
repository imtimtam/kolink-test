from sqlalchemy import ARRAY, String, BigInteger, Date, Text, Column
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base

class pubmed(Base):
    __tablename__ = 'pubmed'

    pmid = Column(BigInteger, primary_key=True)
    publication_types = Column(ARRAY(String), nullable=True)
    title = Column(String, nullable=True)
    journal_title = Column(String, nullable=True)
    authors = Column(JSONB, nullable=True)
    abstract = Column(Text, nullable=True)
    mesh_terms = Column(ARRAY(String), nullable=True)
    date_published = Column(Date, nullable=True)
    lang = Column(String, nullable=True)

class clinicaltrials(Base):
    __tablename__ = 'clinicaltrials'

    nct_id = Column(String, primary_key=True)
    official_title = Column(String, nullable=True)
    brief_title = Column(String, nullable=True)
    org_name = Column(String, nullable=True)
    lead_sponsor = Column(String, nullable=True)
    collaborators = Column(ARRAY(String), nullable=True)
    brief_summary = Column(Text, nullable=True)
    conditions = Column(ARRAY(String), nullable=True)
    keywords = Column(ARRAY(String), nullable=True)
    study_type = Column(String, nullable=True)
    phase = Column(ARRAY(String), nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    zip = Column(String, nullable=True)
    country = Column(String, nullable=True)
    status = Column(String, nullable=True)
    reference_pmid = Column(ARRAY(String), nullable=True)
    start_date = Column(Date, nullable=True)
    completion_date = Column(Date, nullable=True)
    last_updated_post_date = Column(Date, nullable=True)