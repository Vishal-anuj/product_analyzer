from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.analyze import router as analyze_router
from db.mongo import init_mongo_client
import os
from dotenv import load_dotenv


def get_allowed_origins() -> list[str]:
    origins_env = os.getenv("ALLOWED_ORIGINS", "")
    if origins_env.strip() == "*":
        # handled via regex below
        return []
    origins = [o.strip() for o in origins_env.split(",") if o.strip()]
    if not origins:
        # sensible dev defaults
        origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    return origins


load_dotenv()  # Load variables from backend/.env if present

app = FastAPI(title="Product Analyzer API", version="0.1.0")

origins = get_allowed_origins()
allow_origin_regex = None
if not origins and os.getenv("ALLOWED_ORIGINS", "") == "*":
    allow_origin_regex = r"^http://(localhost|127\.0\.0\.1)(:\d+)?$"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    await init_mongo_client()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


app.include_router(analyze_router)


