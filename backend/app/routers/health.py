from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "mydateq-backend",
        "version": "0.2.0",
        "features": [
            "json-analysis",
            "multipart-analysis",
            "waitlist",
        ],
    }
