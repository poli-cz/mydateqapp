from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import ValidationError

from app.schemas.analysis import AnalyzeProfileInput
from app.services.scoring import build_analysis

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze-profile")
async def analyze_profile(request: Request) -> dict[str, Any]:
    """
    Accepts either:
    1) application/json for quick local testing
    2) multipart/form-data for the real upload flow
    """
    content_type = (request.headers.get("content-type") or "").lower()

    try:
        if "multipart/form-data" in content_type:
            form = await request.form()
            photos = form.getlist("photos")
            prompts_raw = form.get("prompts", "[]")

            try:
                parsed_prompts = json.loads(prompts_raw) if isinstance(prompts_raw, str) else []
            except json.JSONDecodeError as exc:
                raise HTTPException(status_code=400, detail="Invalid prompts JSON in multipart form.") from exc

            if not isinstance(parsed_prompts, list):
                raise HTTPException(status_code=400, detail="prompts must be a JSON array.")

            payload = AnalyzeProfileInput(
                platform=str(form.get("platform", "hinge")),
                bio=str(form.get("bio", "")),
                prompts=[str(item) for item in parsed_prompts],
                photo_count=len(photos),
                photo_filenames=[getattr(photo, "filename", "") or "" for photo in photos],
                source="multipart",
            )
        else:
            raw_json = await request.json()
            if not isinstance(raw_json, dict):
                raise HTTPException(status_code=400, detail="JSON payload must be an object.")

            payload = AnalyzeProfileInput(
                platform=str(raw_json.get("platform", "hinge")),
                photo_count=int(raw_json.get("photo_count", 0)),
                bio=str(raw_json.get("bio", "") or ""),
                prompts=[str(item) for item in raw_json.get("prompts", [])],
                photo_filenames=[str(item) for item in raw_json.get("photo_filenames", [])],
                source="demo" if raw_json.get("is_demo") else "json",
            )
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload.") from exc

    result = build_analysis(payload)
    return result.model_dump()
