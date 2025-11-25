from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
import os
from dotenv import load_dotenv

from app.db.models import PubMed
from app.db.models import ClinicalTrials

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    # with engine.begin() as conn:
    #     # python -m app.db.session
    #     PubMed.__table__.drop(conn, checkfirst=True)
    #     ClinicalTrials.__table__.drop(conn, checkfirst=True)

    with Session(engine) as session:
        pass

