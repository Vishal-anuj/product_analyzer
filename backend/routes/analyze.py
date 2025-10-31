from fastapi import APIRouter, HTTPException, Query
from services.analysis_service import analyze_product


router = APIRouter(prefix="", tags=["analyze"])


@router.get("/analyze")
async def analyze(product: str = Query(..., min_length=2)) -> dict:
    try:
        return await analyze_product(product)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


