from typing import Any, Dict, List
from models.product import Product, PriceInfo, Review
from scrapers.amazon import scrape_amazon
from scrapers.flipkart import scrape_flipkart
from services.ollama_client import analyze_reviews_with_ollama, analyze_reviews_by_platform
from db.mongo import get_collection


async def analyze_product(product_query: str) -> Dict[str, Any]:
    normalized = product_query.strip().lower()

    prices: List[PriceInfo] = []
    reviews: List[Review] = []

    # Scrape from multiple platforms
    try:
        amazon_result = await scrape_amazon(product_query)
        prices.extend(amazon_result.get("prices", []))
        reviews.extend(amazon_result.get("reviews", []))
    except Exception:
        # Fail gracefully for this source
        pass

    try:
        flipkart_result = await scrape_flipkart(product_query)
        prices.extend(flipkart_result.get("prices", []))
        reviews.extend(flipkart_result.get("reviews", []))
    except Exception:
        # Fail gracefully for this source
        pass

    # Build product doc
    product = Product(name=product_query, normalized_name=normalized, prices=prices, reviews=reviews)

    # Persist to MongoDB (fail gracefully if DB is unavailable)
    try:
        products_col = get_collection("products")
        reviews_col = get_collection("reviews")

        await products_col.update_one(
            {"normalized_name": normalized},
            {
                "$set": {
                    "name": product.name,
                    "normalized_name": product.normalized_name,
                    "prices": [p.model_dump() for p in product.prices],
                }
            },
            upsert=True,
        )

        if reviews:
            await reviews_col.insert_many([r.model_dump() | {"normalized_name": normalized} for r in reviews])
    except Exception:
        # Proceed without DB persistence
        pass

    # Analysis via Ollama (with safe fallback)
    # Overall analysis
    all_review_texts = [r.content for r in reviews]
    overall_analysis = await analyze_reviews_with_ollama(all_review_texts)

    # Platform-specific sentiment analysis
    platform_analysis = await analyze_reviews_by_platform(reviews)

    response = {
        "product": product.model_dump(),
        "analysis": overall_analysis,
        "platform_comparison": platform_analysis,
    }
    return response


