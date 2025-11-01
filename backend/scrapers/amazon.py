import asyncio
from typing import Dict, Any, List
import httpx
from bs4 import BeautifulSoup  # type: ignore[import-not-found]
from models.product import PriceInfo, Review


# Centralized selector config (to avoid hard-coding throughout codebase)
SELECTORS = {
    "result_item": "div.s-result-item",
    "title": "h2 a span",
    "link": "h2 a",
    "price_whole": "span.a-price-whole",
    "price_fraction": "span.a-price-fraction",
    "review_block": "div[data-hook='review']",
    "review_title": "a[data-hook='review-title'] span",
    "review_content": "span[data-hook='review-body'] span",
    "review_rating": "i[data-hook='review-star-rating'] span",
}


async def search_amazon(query: str) -> str:
    raise NotImplementedError


async def scrape_amazon(query: str) -> Dict[str, Any]:
    # NOTE: For MVP we will simulate a single result and a few reviews to avoid
    # brittle scraping and captchas. Replace with real search + parse later.
    await asyncio.sleep(0)  # yield control

    # Generate varied mock reviews based on query (so each product gets different reviews)
    import hashlib
    query_hash = int(hashlib.md5(query.lower().encode()).hexdigest()[:8], 16)
    
    # Vary ratings and content based on query hash
    base_rating = 3.5 + ((query_hash % 100) / 50.0)  # 3.5 to 5.5 range
    review_variations = [
        (min(5.0, base_rating), "Great find", f"Really happy with my {query}. Quality is excellent and delivery was fast."),
        (max(2.0, base_rating - 1.5), "Could be better", f"{query} works okay but expected more features for the price."),
        (min(5.0, base_rating + 0.3), "Highly recommend", f"Best {query} I've purchased. Exceeded all my expectations!"),
        (max(1.0, base_rating - 2.0), "Disappointing", f"Not satisfied with {query}. Build quality is poor and stopped working after a week."),
        (base_rating, "Decent product", f"{query} is average. Does the job but nothing special."),
    ]
    
    prices: List[PriceInfo] = [
        PriceInfo(
            platform="Amazon", 
            url="https://www.amazon.in/s?k=" + query.replace(" ", "+"), 
            price=float(9999 + (query_hash % 50000)),
            currency="INR"
        ),
    ]
    
    reviews: List[Review] = [
        Review(platform="Amazon", rating=rating, title=title, content=content)
        for rating, title, content in review_variations[:3]  # Return 3 varied reviews
    ]
    return {"prices": prices, "reviews": reviews}


