import os
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


_client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None


async def init_mongo_client() -> None:
    global _client, db  # noqa: PLW0603
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    database = os.getenv("MONGODB_DB", "product_analyzer")
    _client = AsyncIOMotorClient(uri)
    db = _client[database]


def get_collection(name: str):  # type: ignore[no-untyped-def]
    if db is None:
        raise RuntimeError("MongoDB not initialized")
    return db[name]


