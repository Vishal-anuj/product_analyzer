from typing import Dict, Any


async def graceful_scrape(scrape_fn, *args, **kwargs) -> Dict[str, Any]:  # type: ignore[no-untyped-def]
    try:
        return await scrape_fn(*args, **kwargs)
    except Exception:
        return {"prices": [], "reviews": []}


