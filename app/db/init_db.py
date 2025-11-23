from .session import engine
from .models import PubMed, ClinicalTrials
from .base import Base

# JUST NEED TO CALL ONCE TO CREATE TABLES
# python -m app.db.init_db
Base.metadata.create_all(bind=engine)