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

    prices: List[PriceInfo] = [
        PriceInfo(platform="Amazon", url="https://www.amazon.in/s?k=" + query, price=None),
    ]
    reviews: List[Review] = [
        Review(platform="Amazon", rating=4.0, title="Good", content=f"{query} is pretty decent."),
        Review(platform="Amazon", rating=2.0, title="Average", content=f"{query} has some issues."),
    ]
    return {"prices": prices, "reviews": reviews}


