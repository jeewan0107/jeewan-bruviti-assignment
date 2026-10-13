from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.schemas import DecisionRequest, DecisionResponse
from app.decision import decide

ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="Repair vs Replace Classification", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/decide", response_model=DecisionResponse)
def decide_endpoint(case: DecisionRequest):
    return decide(case)

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(str(ROOT / "static" / "index.html"))
