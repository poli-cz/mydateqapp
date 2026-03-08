from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.analysis import router as analysis_router
from app.routers.health import router as health_router
from app.routers.waitlist import router as waitlist_router

app = FastAPI(
    title="MyDateQ API",
    version="0.2.0",
    description="MVP backend for the MyDateQ dating profile analysis application.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://www.mydateq.com",
        "https://mydateq.com",
        "https://app.mydateq.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(analysis_router)
app.include_router(waitlist_router)


@app.get("/")
def root() -> dict:
    return {
        "message": "MyDateQ backend is running.",
        "docs": "/docs",
        "health": "/api/health",
    }
