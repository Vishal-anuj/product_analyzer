import os
import httpx
import re
import logging
from typing import List, Dict, Any
from collections import defaultdict
from models.product import Review

logger = logging.getLogger(__name__)

# Hugging Face API configuration - read at runtime to ensure env vars are loaded
def get_hf_config():
    """Get Hugging Face configuration, reading env vars at runtime."""
    return {
        "api_base": os.getenv("HF_API_BASE", "https://api-inference.huggingface.co/models"),
        "api_token": os.getenv("HF_API_TOKEN", "").strip() if os.getenv("HF_API_TOKEN") else "",
        "model": os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.2"),
    }

PROMPT_TEMPLATE = (
    "You are a product review analyzer. Given raw reviews, return ONLY valid JSON (no markdown, no code blocks) with keys: "
    "sentiment (percentages for positive, neutral, negative), pros (array), cons (array), "
    "score (1-10), best_platform (string). Consider aspects like battery, build, camera, delivery, etc.\n\n"
    "REVIEWS:\n{reviews}\n\n"
    "Return ONLY the JSON object, nothing else:"
)

PLATFORM_PROMPT_TEMPLATE = (
    "Analyze the sentiment of these product reviews from {platform}. "
    "Return ONLY valid JSON (no markdown, no code blocks) with keys: sentiment (percentages for positive, neutral, negative), "
    "average_rating (float), overall_sentiment (one word: positive/neutral/negative).\n\n"
    "REVIEWS:\n{reviews}\n\n"
    "Return ONLY the JSON object, nothing else:"
)


def extract_json_from_response(text: str) -> Dict[str, Any]:
    """Extract JSON from response, handling markdown code blocks and extra text."""
    import json as _json
    
    # Try direct parsing first
    try:
        return _json.loads(text.strip())
    except Exception:
        pass
    
    # Try to extract JSON from markdown code blocks
    json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        try:
            return _json.loads(match.group(1))
        except Exception:
            pass
    
    # Try to find JSON object in text
    brace_match = re.search(r'\{.*\}', text, re.DOTALL)
    if brace_match:
        try:
            return _json.loads(brace_match.group(0))
        except Exception:
            pass
    
    raise ValueError(f"Could not parse JSON from response: {text[:200]}")


async def analyze_reviews_with_huggingface(reviews: List[str]) -> Dict[str, Any]:
    """Analyze reviews using Hugging Face Inference API."""
    if not reviews:
        return {
            "sentiment": {"positive": 0, "neutral": 100, "negative": 0},
            "pros": [],
            "cons": [],
            "score": 5,
            "best_platform": None,
        }

    config = get_hf_config()
    model = config["model"]
    api_base = config["api_base"]
    
    # Check if this is a custom Hugging Face Space (ends with .hf.space)
    is_custom_space = ".hf.space" in api_base or "hf.space" in api_base
    
    if is_custom_space:
        # Custom Space endpoint - use /analyze endpoint
        api_url = f"{api_base}/analyze" if not api_base.endswith("/analyze") else api_base
    else:
        # Standard Inference API
        api_url = f"{api_base}/{model}" if model else api_base
    
    reviews_text = "\n---\n".join(reviews[:50])
    prompt = PROMPT_TEMPLATE.format(reviews=reviews_text)

    logger.info(f"Querying Hugging Face API at {api_url} with model {model} for {len(reviews)} reviews")
    
    headers = {
        "Content-Type": "application/json",
    }
    token = config["api_token"]
    if token:
        headers["Authorization"] = f"Bearer {token}"
        logger.info("Using Hugging Face API token for authenticated request")
    else:
        logger.warning("No Hugging Face API token found - requests may be rate limited")

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            if is_custom_space:
                # Custom Space API - expects {"reviews": [...]}
                resp = await client.post(
                    api_url,
                    headers=headers,
                    json={"reviews": reviews[:50]},
                )
            elif "instruct" in model.lower() or "chat" in model.lower():
                # For chat models (like Llama), use chat endpoint format
                resp = await client.post(
                    api_url,
                    headers=headers,
                    json={
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": 500,
                            "temperature": 0.7,
                            "return_full_text": False,
                        },
                    },
                )
            else:
                # For other models, use standard format
                resp = await client.post(
                    api_url,
                    headers=headers,
                    json={"inputs": reviews_text},
                )
            
            # Handle rate limiting (model loading)
            if resp.status_code == 503:
                logger.warning("Model is loading, waiting...")
                import asyncio
                await asyncio.sleep(10)
                resp = await client.post(api_url, headers=headers, json={"inputs": reviews_text})
            
            resp.raise_for_status()
            data = resp.json()
            
            # Handle custom Space response (direct JSON with sentiment, pros, cons, score)
            if is_custom_space:
                logger.info(f"Custom Space response received: {data}")
                # Custom Space should return the expected format directly
                if isinstance(data, dict) and "sentiment" in data:
                    return {
                        "sentiment": data.get("sentiment", {"positive": 0, "neutral": 0, "negative": 0}),
                        "pros": data.get("pros", []),
                        "cons": data.get("cons", []),
                        "score": data.get("score", 5.0),
                        "best_platform": data.get("best_platform"),
                    }
            
            # Handle different response formats for Inference API
            if isinstance(data, list) and len(data) > 0:
                # Standard HF response: [{"generated_text": "..."}]
                text = data[0].get("generated_text", "")
            elif isinstance(data, dict):
                text = data.get("generated_text", "") or data.get("text", "") or str(data)
            else:
                text = str(data)
            
            logger.info(f"Hugging Face response received: {text[:200]}...")
            
            try:
                parsed = extract_json_from_response(text)
                logger.info("Successfully parsed JSON from Hugging Face response")
                return parsed
            except Exception as parse_err:
                logger.warning(f"Failed to parse JSON from Hugging Face response: {parse_err}. Response: {text[:500]}")
                return {
                    "sentiment": {"positive": 33, "neutral": 34, "negative": 33},
                    "pros": [],
                    "cons": [],
                    "score": 6.5,
                    "best_platform": None,
                    "raw": text[:500],
                    "parse_error": str(parse_err),
                }
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error from Hugging Face API: {e.response.status_code} - {e.response.text[:200]}")
        return calculate_sentiment_fallback(reviews)
    except httpx.TimeoutException:
        logger.error("Hugging Face request timed out. Using fallback.")
        return calculate_sentiment_fallback(reviews)
    except Exception as e:
        logger.error(f"Error querying Hugging Face API: {e}. Using fallback.")
        return calculate_sentiment_fallback(reviews)

# Alias for backward compatibility
analyze_reviews_with_ollama = analyze_reviews_with_huggingface


def calculate_sentiment_fallback(reviews: List[str]) -> Dict[str, Any]:
    """Calculate basic sentiment from review keywords when Hugging Face is unavailable."""
    positive_keywords = ["good", "great", "excellent", "love", "amazing", "perfect", "best", "satisfied", "happy", "recommend", "fantastic", "superb", "awesome", "wonderful"]
    negative_keywords = ["bad", "terrible", "worst", "hate", "disappointed", "poor", "awful", "broken", "defective", "return", "regret", "disappointing", "horrible"]
    
    # Extract pros and cons from reviews
    pros_keywords = {
        "quality": ["excellent quality", "build quality", "solid build", "durable", "well built", "premium"],
        "performance": ["fast", "performance", "powerful", "smooth", "responsive", "quick"],
        "value": ["value for money", "worth it", "affordable", "great price", "budget friendly"],
        "features": ["features", "functionality", "versatile", "useful"],
        "service": ["fast shipping", "delivery", "customer service", "support"],
    }
    
    cons_keywords = {
        "quality": ["poor quality", "cheap", "broke", "stopped working", "defective"],
        "performance": ["slow", "laggy", "freezes", "doesn't work", "issues"],
        "price": ["overpriced", "expensive", "not worth", "too costly"],
        "features": ["missing features", "lack of", "no", "without"],
        "service": ["poor service", "delayed", "shipping issues", "no support"],
    }
    
    positive_count = sum(1 for review in reviews if any(kw in review.lower() for kw in positive_keywords))
    negative_count = sum(1 for review in reviews if any(kw in review.lower() for kw in negative_keywords))
    total = len(reviews)
    neutral_count = total - positive_count - negative_count
    
    if total > 0:
        pos_pct = int((positive_count / total) * 100)
        neg_pct = int((negative_count / total) * 100)
        neu_pct = 100 - pos_pct - neg_pct
    else:
        pos_pct = neg_pct = 33
        neu_pct = 34
    
    # Extract actual pros and cons from reviews
    pros = []
    cons = []
    
    for review in reviews:
        review_lower = review.lower()
        # Check for pros
        for category, keywords in pros_keywords.items():
            if any(kw in review_lower for kw in keywords):
                if category.capitalize() not in pros:
                    pros.append(category.capitalize())
        
        # Check for cons
        for category, keywords in cons_keywords.items():
            if any(kw in review_lower for kw in keywords):
                if category.capitalize() not in cons:
                    cons.append(category.capitalize())
    
    # Fallback pros/cons if none found
    if not pros and pos_pct > neg_pct:
        pros = ["Overall positive sentiment", "Good customer feedback"]
    if not cons and neg_pct > 0:
        cons = ["Some concerns mentioned in reviews"]
    
    # Calculate score (1-10)
    score = 5.0 + (pos_pct - neg_pct) / 20.0
    score = max(1.0, min(10.0, score))
    
    return {
        "sentiment": {"positive": pos_pct, "neutral": neu_pct, "negative": neg_pct},
        "pros": pros if pros else ["Positive aspects identified from reviews"],
        "cons": cons if cons else ["No major concerns identified"],
        "score": round(score, 1),
        "best_platform": None,
    }


def calculate_rating_sentiment(avg_rating: float | None) -> Dict[str, int]:
    """Calculate sentiment percentages based on average rating."""
    if avg_rating is None:
        return {"positive": 0, "neutral": 0, "negative": 0}
    if avg_rating >= 4.0:
        return {"positive": 70, "neutral": 20, "negative": 10}
    elif avg_rating >= 3.0:
        return {"positive": 30, "neutral": 50, "negative": 20}
    else:
        return {"positive": 10, "neutral": 30, "negative": 60}


async def analyze_reviews_by_platform(reviews: List[Review]) -> Dict[str, Any]:
    """Analyze reviews grouped by platform to compare sentiment across platforms."""
    if not reviews:
        return {
            "platforms": [],
            "comparison": {},
        }

    # Group reviews by platform
    platform_reviews: Dict[str, List[str]] = defaultdict(list)
    platform_ratings: Dict[str, List[float]] = defaultdict(list)
    
    for review in reviews:
        platform_reviews[review.platform].append(review.content)
        if review.rating:
            platform_ratings[review.platform].append(review.rating)

    # Analyze each platform
    platform_results: Dict[str, Dict[str, Any]] = {}
    config = get_hf_config()
    model = config["model"]
    api_base = config["api_base"]
    
    # Check if this is a custom Hugging Face Space
    is_custom_space = ".hf.space" in api_base or "hf.space" in api_base
    
    if is_custom_space:
        api_url = f"{api_base}/analyze" if not api_base.endswith("/analyze") else api_base
    else:
        api_url = f"{api_base}/{model}" if model else api_base
    
    headers = {
        "Content-Type": "application/json",
    }
    token = config["api_token"]
    if token:
        headers["Authorization"] = f"Bearer {token}"

    for platform, review_texts in platform_reviews.items():
        # Calculate average rating if available
        avg_rating = None
        if platform_ratings[platform]:
            avg_rating = sum(platform_ratings[platform]) / len(platform_ratings[platform])

        # Get sentiment analysis from Hugging Face
        prompt = PLATFORM_PROMPT_TEMPLATE.format(
            platform=platform,
            reviews="\n---\n".join(review_texts[:30])  # Limit to 30 reviews per platform
        )

        logger.info(f"Querying Hugging Face for {platform} platform with {len(review_texts)} reviews")
        
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                if is_custom_space:
                    # Custom Space API
                    resp = await client.post(
                        api_url,
                        headers=headers,
                        json={"reviews": review_texts[:30]},
                    )
                elif "instruct" in model.lower() or "chat" in model.lower():
                    # For chat models
                    resp = await client.post(
                        api_url,
                        headers=headers,
                        json={
                            "inputs": prompt,
                            "parameters": {
                                "max_new_tokens": 300,
                                "temperature": 0.7,
                                "return_full_text": False,
                            },
                        },
                    )
                else:
                    resp = await client.post(
                        api_url,
                        headers=headers,
                        json={"inputs": "\n---\n".join(review_texts[:30])},
                    )
                
                # Handle rate limiting
                if resp.status_code == 503:
                    logger.warning(f"Model loading for {platform}, using fallback")
                    sentiment = calculate_rating_sentiment(avg_rating)
                    platform_results[platform] = {
                        "sentiment": sentiment,
                        "average_rating": avg_rating or 0.0,
                        "review_count": len(review_texts),
                        "overall_sentiment": "positive" if avg_rating and avg_rating >= 4.0 else ("negative" if avg_rating and avg_rating < 3.0 else "neutral"),
                    }
                    continue
                
                resp.raise_for_status()
                data = resp.json()
                
                # Handle custom Space response
                if is_custom_space and isinstance(data, dict) and "sentiment" in data:
                    platform_results[platform] = {
                        "sentiment": data.get("sentiment", {"positive": 0, "neutral": 0, "negative": 0}),
                        "average_rating": avg_rating or 0.0,
                        "review_count": len(review_texts),
                        "overall_sentiment": "positive" if data.get("sentiment", {}).get("positive", 0) > 50 else ("negative" if data.get("sentiment", {}).get("negative", 0) > 50 else "neutral"),
                    }
                    logger.info(f"Successfully processed custom Space response for {platform}")
                    continue
                
                # Handle different response formats for Inference API
                if isinstance(data, list) and len(data) > 0:
                    text = data[0].get("generated_text", "")
                elif isinstance(data, dict):
                    text = data.get("generated_text", "") or data.get("text", "") or str(data)
                else:
                    text = str(data)
                
                logger.info(f"Hugging Face response for {platform}: {text[:200]}...")
                
                try:
                    parsed = extract_json_from_response(text)
                    platform_results[platform] = {
                        "sentiment": parsed.get("sentiment", {"positive": 0, "neutral": 0, "negative": 0}),
                        "average_rating": avg_rating or parsed.get("average_rating", 0.0),
                        "review_count": len(review_texts),
                        "overall_sentiment": parsed.get("overall_sentiment", "neutral"),
                    }
                    logger.info(f"Successfully parsed Hugging Face response for {platform}")
                except Exception as parse_err:
                    logger.warning(f"Failed to parse JSON for {platform}: {parse_err}")
                    # Fallback: calculate sentiment from ratings if available
                    sentiment = calculate_rating_sentiment(avg_rating)
                    platform_results[platform] = {
                        "sentiment": sentiment,
                        "average_rating": avg_rating or 0.0,
                        "review_count": len(review_texts),
                        "overall_sentiment": "positive" if avg_rating and avg_rating >= 4.0 else ("negative" if avg_rating and avg_rating < 3.0 else "neutral"),
                    }
        except (httpx.HTTPStatusError, httpx.TimeoutException) as e:
            logger.warning(f"Hugging Face unavailable for {platform}: {e}. Using rating-based fallback.")
            sentiment = calculate_rating_sentiment(avg_rating)
            platform_results[platform] = {
                "sentiment": sentiment,
                "average_rating": avg_rating or 0.0,
                "review_count": len(review_texts),
                "overall_sentiment": "positive" if avg_rating and avg_rating >= 4.0 else ("negative" if avg_rating and avg_rating < 3.0 else "neutral"),
            }
        except Exception as e:
            logger.error(f"Unexpected error querying Hugging Face for {platform}: {e}")
            sentiment = calculate_rating_sentiment(avg_rating)
            platform_results[platform] = {
                "sentiment": sentiment,
                "average_rating": avg_rating or 0.0,
                "review_count": len(review_texts),
                "overall_sentiment": "positive" if avg_rating and avg_rating >= 4.0 else ("negative" if avg_rating and avg_rating < 3.0 else "neutral"),
            }

    # Determine best platform based on sentiment and ratings
    best_platform = None
    best_score = -1
    for platform, data in platform_results.items():
        score = data.get("sentiment", {}).get("positive", 0) + (data.get("average_rating", 0) * 10)
        if score > best_score:
            best_score = score
            best_platform = platform

    return {
        "platforms": list(platform_results.keys()),
        "comparison": platform_results,
        "best_platform": best_platform,
    }


