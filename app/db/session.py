from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

with Session(engine) as session:
    pass


