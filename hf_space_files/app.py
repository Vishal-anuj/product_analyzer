"""
FastAPI app for Hugging Face Space deployment.
This provides a sentiment analysis API endpoint.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load sentiment analysis model
model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
sentiment_pipeline = None

@app.on_event("startup")
async def load_model():
    """Load the sentiment analysis model on startup."""
    global sentiment_pipeline
    try:
        logger.info(f"Loading model: {model_name}")
        sentiment_pipeline = pipeline("sentiment-analysis", model=model_name, device=-1)
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        sentiment_pipeline = None

class AnalyzeRequest(BaseModel):
    reviews: list[str]

class SentimentResponse(BaseModel):
    sentiment: dict
    pros: list[str]
    cons: list[str]
    score: float
    best_platform: str | None = None

@app.get("/")
def read_root():
    return {
        "status": "ready", 
        "model": "cardiffnlp/twitter-roberta-base-sentiment-latest",
        "endpoint": "/analyze"
    }

@app.post("/analyze", response_model=SentimentResponse)
async def analyze_reviews(request: AnalyzeRequest):
    """Analyze reviews and return sentiment + pros/cons"""
    if not sentiment_pipeline:
        raise Exception("Model not loaded")
    
    reviews = request.reviews[:50]  # Limit to 50 reviews
    reviews_text = "\n".join(reviews)
    
    # Analyze sentiment for each review (limit text length)
    try:
        # Process reviews in batches to avoid token limits
        all_results = []
        for review in reviews:
            if len(review) > 512:
                review = review[:512]
            try:
                result = sentiment_pipeline(review)
                all_results.append(result[0] if isinstance(result, list) else result)
            except Exception as e:
                logger.warning(f"Error analyzing review: {e}")
                continue
        
        # Calculate percentages
        positive = sum(1 for r in all_results if r.get('label', '').upper() in ['POSITIVE', 'LABEL_2', 'LABEL_1'])
        negative = sum(1 for r in all_results if r.get('label', '').upper() in ['NEGATIVE', 'LABEL_0'])
        neutral = len(all_results) - positive - negative
        
        total = len(all_results) if all_results else 1
        pos_pct = int((positive / total) * 100) if total > 0 else 0
        neg_pct = int((negative / total) * 100) if total > 0 else 0
        neu_pct = 100 - pos_pct - neg_pct
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        pos_pct = neg_pct = 33
        neu_pct = 34
    
    # Extract pros/cons using keyword matching
    pros_keywords = {
        "Quality": ["excellent quality", "build quality", "solid build", "durable", "well built", "premium", "great quality"],
        "Performance": ["fast", "performance", "powerful", "smooth", "responsive", "quick", "works well"],
        "Value": ["value for money", "worth it", "affordable", "great price", "budget friendly", "good value"],
        "Features": ["features", "functionality", "versatile", "useful", "convenient"],
        "Service": ["fast shipping", "delivery", "customer service", "support", "quick delivery"],
    }
    
    cons_keywords = {
        "Quality Issues": ["poor quality", "cheap", "broke", "stopped working", "defective", "broken"],
        "Performance Problems": ["slow", "laggy", "freezes", "doesn't work", "issues", "problems"],
        "Pricing Concerns": ["overpriced", "expensive", "not worth", "too costly", "pricey"],
        "Missing Features": ["missing features", "lack of", "no", "without"],
        "Service Issues": ["poor service", "delayed", "shipping issues", "no support", "slow delivery"],
    }
    
    pros = []
    cons = []
    
    for review in reviews:
        review_lower = review.lower()
        # Check for pros
        for category, keywords in pros_keywords.items():
            if any(kw in review_lower for kw in keywords):
                if category not in pros:
                    pros.append(category)
        
        # Check for cons
        for category, keywords in cons_keywords.items():
            if any(kw in review_lower for kw in keywords):
                if category not in cons:
                    cons.append(category)
    
    # Fallback pros/cons if none found
    if not pros and pos_pct > neg_pct:
        pros = ["Overall positive sentiment"]
    if not cons and neg_pct > 0:
        cons = ["Some concerns mentioned"]
    if not pros:
        pros = ["Positive aspects identified"]
    if not cons:
        cons = ["No major concerns identified"]
    
    # Calculate score (1-10)
    score = 5.0 + (pos_pct - neg_pct) / 20.0
    score = max(1.0, min(10.0, score))
    
    return SentimentResponse(
        sentiment={"positive": pos_pct, "neutral": neu_pct, "negative": neg_pct},
        pros=pros[:5],  # Limit to 5 pros
        cons=cons[:5],  # Limit to 5 cons
        score=round(score, 1),
        best_platform=None
    )

# The app will be run by uvicorn command in Dockerfile

