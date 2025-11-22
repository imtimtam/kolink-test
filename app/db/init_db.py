from .session import engine
from .models import pubmed, clinicaltrials
from .base import Base

Base.metadata.create_all(bind=engine)