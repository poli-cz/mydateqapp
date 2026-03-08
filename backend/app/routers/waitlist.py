from __future__ import annotations

import csv
import re
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api", tags=["waitlist"])

DATA_DIR = Path("data")
WAITLIST_FILE = DATA_DIR / "waitlist.csv"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class WaitlistRequest(BaseModel):
    email: str = Field(..., max_length=254)
    source: str = Field(default="dateq-app")
    analysis_id: str | None = None


@router.post("/waitlist")
def join_waitlist(payload: WaitlistRequest) -> dict:
    email = payload.email.strip().lower()
    if not EMAIL_RE.match(email):
        raise HTTPException(status_code=400, detail="Invalid email address.")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    is_new = True

    if WAITLIST_FILE.exists():
        with WAITLIST_FILE.open("r", newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                if row.get("email", "").strip().lower() == email:
                    is_new = False
                    break

    if is_new:
        file_exists = WAITLIST_FILE.exists()
        with WAITLIST_FILE.open("a", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=["email", "source", "analysis_id", "created_at_utc"])
            if not file_exists:
                writer.writeheader()
            writer.writerow(
                {
                    "email": email,
                    "source": payload.source,
                    "analysis_id": payload.analysis_id or "",
                    "created_at_utc": datetime.now(timezone.utc).isoformat(),
                }
            )

    return {
        "ok": True,
        "status": "subscribed" if is_new else "already_subscribed",
        "email": email,
    }
