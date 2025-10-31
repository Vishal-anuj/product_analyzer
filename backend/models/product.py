from pydantic import BaseModel, Field
from typing import Optional, List


class PriceInfo(BaseModel):
    platform: str
    url: Optional[str] = None
    price: Optional[float] = None
    currency: str = "INR"


class Review(BaseModel):
    platform: str
    rating: Optional[float] = None
    title: Optional[str] = None
    content: str


class Product(BaseModel):
    name: str
    normalized_name: str = Field(..., description="lowercased normalized key")
    prices: List[PriceInfo] = []
    reviews: List[Review] = []


class AnalysisResult(BaseModel):
    sentiment: dict
    pros: List[str]
    cons: List[str]
    score: float
    best_platform: Optional[str]


class AnalyzeResponse(BaseModel):
    product: Product
    analysis: AnalysisResult


