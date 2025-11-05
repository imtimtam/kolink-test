from fastapi import FastAPI
from app.routes import pubmed_routes

app = FastAPI()
app.include_router(pubmed_routes.router, prefix="/pubmed")

@app.get("/")
def test():
    return {"message": "API is working!"}