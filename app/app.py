from fastapi import FastAPI
from app.routes import clinicaltrials_routes, pubmed_routes

app = FastAPI()
app.include_router(pubmed_routes.router)
app.include_router(clinicaltrials_routes.router)