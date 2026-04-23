from fastapi import FastAPI
from service import run_ingestion

app = FastAPI()

@app.get("/")
def root():
    return {"status": "AlphaGenome-compatible backend running"}

@app.post("/ingest")
def ingest():

    result = run_ingestion()

    return {
        "message": "ingestion complete",
        "graph_stats": result
    }
