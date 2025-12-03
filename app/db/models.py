from sqlalchemy import ARRAY, Integer, String, Date, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
from datetime import date

class PubMed(Base):
    __tablename__ = 'pubmed'

    pmid: Mapped[int] = mapped_column(Integer, primary_key=True)
    publication_types: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    journal_title: Mapped[str | None] = mapped_column(String, nullable=True)
    authors: Mapped[dict] = mapped_column(JSONB, nullable=False)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)
    mesh_terms: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    date_published: Mapped[date | None] = mapped_column(Date, nullable=True)
    language: Mapped[str | None] = mapped_column(String, nullable=True)

class ClinicalTrials(Base):
    __tablename__ = 'clinicaltrials'
    # Potentially swap to Optional[...] later
    nct_id: Mapped[str] = mapped_column(String, primary_key=True)
    official_title: Mapped[str | None] = mapped_column(String, nullable=True)
    brief_title: Mapped[str] = mapped_column(String, nullable=False)
    org_name: Mapped[str | None] = mapped_column(String, nullable=True)
    lead_sponsor: Mapped[str | None] = mapped_column(String, nullable=True)
    collaborators: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    brief_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    conditions: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    keywords: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    study_type: Mapped[str | None] = mapped_column(String, nullable=True)
    phase: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    city: Mapped[str | None] = mapped_column(String, nullable=True)
    state: Mapped[str | None] = mapped_column(String, nullable=True)
    zip: Mapped[str | None] = mapped_column(String, nullable=True)
    country: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)
    reference_pmid: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completion_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_update_post_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    
    # OLD
    # nct_id = Column(String, primary_key=True)
    # official_title = Column(String, nullable=True)
    # brief_title = Column(String, nullable=False)
    # org_name = Column(String, nullable=True)
    # lead_sponsor = Column(String, nullable=True)
    # collaborators = Column(ARRAY(String), nullable=True)
    # brief_summary = Column(Text, nullable=True)
    # conditions = Column(ARRAY(String), nullable=True)
    # keywords = Column(ARRAY(String), nullable=True)
    # study_type = Column(String, nullable=True)
    # phase = Column(ARRAY(String), nullable=True)
    # city = Column(String, nullable=True)
    # state = Column(String, nullable=True)
    # zip = Column(String, nullable=True)
    # country = Column(String, nullable=True)
    # status = Column(String, nullable=True)
    # reference_pmid = Column(ARRAY(String), nullable=True)
    # start_date = Column(Date, nullable=True)
    # completion_date = Column(Date, nullable=True)
    # last_update_post_date = Column(Date, nullable=True)