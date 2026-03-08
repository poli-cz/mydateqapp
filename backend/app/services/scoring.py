from __future__ import annotations

import re
import uuid
from typing import Iterable

from app.schemas.analysis import (
    AnalysisResponse,
    AnalyzeProfileInput,
    FreeReport,
    LookingForTag,
    OpenerItem,
    PhotoBreakdownItem,
    PhotoScorePreview,
    ProReport,
)

GENERIC_PHRASES = {
    "just ask",
    "fluent in sarcasm",
    "here for a good time",
    "partner in crime",
    "love to travel",
    "work hard play hard",
}

SPECIFIC_WORDS = {
    "brunch",
    "dumpling",
    "carbonara",
    "rooftop",
    "climbing",
    "vinyl",
    "museum",
    "bookstore",
    "espresso",
    "ceramics",
    "farmers market",
    "tacos",
    "ramen",
    "surf",
    "dog",
    "hike",
    "tennis",
    "jazz",
}

PLATFORM_TIPS = {
    "hinge": "Hinge rewards comments over likes. Give people one concrete detail they can reply to.",
    "bumble": "Bumble works best when your profile signals easy first messages and low-friction conversation starters.",
    "tinder": "On Tinder the first photo matters most. Clear, confident photos beat vague personality claims.",
}

LOOKING_FOR_MAP = [
    ("🎯", "Playful"),
    ("🍝", "Foodie"),
    ("🌆", "City dates"),
    ("🗣️", "Good banter"),
]


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z']+", text.lower())



def _count_specificity_hits(text: str) -> int:
    lowered = text.lower()
    hits = sum(1 for phrase in SPECIFIC_WORDS if phrase in lowered)
    hits += len(re.findall(r"\b\d{1,2}(am|pm)?\b", lowered))
    hits += len(re.findall(r"\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", lowered))
    return hits



def _has_generic_phrase(text: str) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in GENERIC_PHRASES)



def _photo_signals(photo_names: Iterable[str], photo_count: int) -> tuple[float, list[PhotoBreakdownItem], list[PhotoScorePreview]]:
    filenames = [name.lower() for name in photo_names]

    base = 5.2 + min(photo_count, 6) * 0.35
    notes: list[PhotoBreakdownItem] = []

    if photo_count == 0:
        notes.append(
            PhotoBreakdownItem(
                label="Missing photos",
                score=3.8,
                note="No photos were uploaded, so the result is conservative and based mostly on text.",
                action="Upload 4 to 6 photos for a real ranking and better recommendations.",
            )
        )
    else:
        for idx in range(photo_count):
            name = filenames[idx] if idx < len(filenames) else f"photo_{idx + 1}.jpg"
            score = 6.2 + min(idx, 3) * 0.25
            note = "Good baseline photo."
            action = "Keep if this reflects your current look."

            if any(term in name for term in ["group", "friends", "party"]):
                score -= 1.2
                note = "Group-style filename suggests lower clarity around who you are."
                action = "Use a clear solo photo earlier in the stack."
            elif any(term in name for term in ["mirror", "gym", "car"]):
                score -= 0.6
                note = "This likely reads as more common or lower-effort unless the shot is unusually strong."
                action = "Swap for a candid outdoor or social-context image."
            elif any(term in name for term in ["dog", "hike", "travel", "beach", "surf"]):
                score += 0.6
                note = "Lifestyle signal helps give strangers something to comment on."
                action = "Keep this later in the stack to add range and personality."
            elif idx == 0:
                score += 0.5
                note = "First photo slot is valuable; assume this is the main first impression image."
                action = "Make sure this is bright, solo, and face-forward."

            score = round(max(3.5, min(score, 8.8)), 1)
            notes.append(
                PhotoBreakdownItem(
                    label=f"Photo {idx + 1}",
                    score=score,
                    note=note,
                    action=action,
                )
            )

    if photo_count < 4:
        base -= 0.5
    elif photo_count >= 5:
        base += 0.3

    avg_score = round(max(3.8, min(base, 8.8)), 1)
    preview = [
        PhotoScorePreview(label=item.label, score=item.score, note=item.note)
        for item in notes[: min(4, len(notes))]
    ]

    return avg_score, notes, preview



def _bio_score_and_rewrite(bio: str, platform: str) -> tuple[float, str, str, str]:
    bio = (bio or "").strip()
    if not bio:
        rewrite = "Curious, warm, and easy to take out. I plan good dates, ask better questions, and can usually find the best spot on any menu."
        return 4.7, "Your profile is missing a written hook.", rewrite, "Add one specific detail and one dateable invitation."

    tokens = _tokenize(bio)
    specificity = _count_specificity_hits(bio)
    generic_penalty = 0.8 if _has_generic_phrase(bio) else 0.0
    length_bonus = 0.6 if 18 <= len(tokens) <= 45 else (0.2 if len(tokens) >= 10 else -0.4)
    specificity_bonus = min(1.5, specificity * 0.35)
    score = round(max(4.5, min(8.7, 5.1 + length_bonus + specificity_bonus - generic_penalty)), 1)

    first_sentence = bio.split("\n")[0].strip().rstrip(".")
    hook = first_sentence if len(first_sentence) < 90 else "Software engineer with better date ideas than small talk"
    rewrite = (
        f"{hook}. I’m best in places with a little momentum — hidden brunch spots, rooftop bars,"
        f" and plans that feel specific enough to actually happen."
    )
    rewrite += " I’ll happily pick the spot if you bring one strong opinion and one unexpectedly good story."

    headline = (
        "There is real personality here, but it is not packaged into a clean reply-worthy hook."
        if score >= 6.6
        else "The bio gives some signal, but it still reads more generic than memorable."
    )
    action = (
        PLATFORM_TIPS.get(platform.lower(), PLATFORM_TIPS["hinge"])
        if specificity < 2
        else "Keep the personality, but compress it into one sharper lead line and one concrete date cue."
    )
    return score, headline, rewrite, action



def _prompt_score_and_openers(prompts: list[str], bio: str, platform: str) -> tuple[float, list[OpenerItem], list[OpenerItem]]:
    clean_prompts = [p.strip() for p in prompts if p and p.strip()]
    if not clean_prompts:
        generic = [
            OpenerItem(
                prompt="Comment on their prompt",
                text="Pick one detail they mention and ask about the story behind it instead of just complimenting it.",
            ),
            OpenerItem(
                prompt="Bio follow-up",
                text="Use the most specific line in your bio as the seed for your first date conversation.",
            ),
        ]
        return 4.9, generic[:1], generic

    specificity_hits = sum(_count_specificity_hits(p) for p in clean_prompts)
    generic_count = sum(1 for p in clean_prompts if _has_generic_phrase(p))
    score = round(max(4.9, min(8.5, 5.4 + min(1.4, specificity_hits * 0.3) - generic_count * 0.35)), 1)

    source_text = " ".join(clean_prompts) + " " + bio
    theme = "food" if any(word in source_text.lower() for word in ["cook", "brunch", "restaurant", "ramen", "dumpling", "taco"]) else "adventure"

    if theme == "food":
        openers = [
            OpenerItem(
                prompt="Comment on their prompt",
                text="You mentioned hidden brunch spots — are you actually gatekeeping one elite place or just emotionally attached to eggs Benedict?",
            ),
            OpenerItem(
                prompt="Photo comment",
                text="Your food photo raises an important question: are you better at finding places or ordering the right thing once you get there?",
            ),
            OpenerItem(
                prompt="Bio follow-up",
                text="You offered to cook by date three, which is bold. What is the signature dish that gets you invited back for date four?",
            ),
        ]
    else:
        openers = [
            OpenerItem(
                prompt="Comment on their prompt",
                text="Your profile gives mildly dangerous ‘I will talk me into a spontaneous plan’ energy. What kind of plan are we talking about exactly?",
            ),
            OpenerItem(
                prompt="Photo comment",
                text="This photo feels like there is a better story behind it than the picture itself — what was happening five minutes before it was taken?",
            ),
            OpenerItem(
                prompt="Bio follow-up",
                text="You seem fun in a very specific way. What is the kind of date you instantly say yes to?",
            ),
        ]

    return score, openers[:2], openers



def _platform_fit(platform: str) -> float:
    platform = (platform or "hinge").lower()
    if platform == "hinge":
        return 7.2
    if platform == "bumble":
        return 6.8
    if platform == "tinder":
        return 6.6
    return 6.4



def build_analysis(payload: AnalyzeProfileInput) -> AnalysisResponse:
    photo_quality, photo_breakdown, photo_preview = _photo_signals(payload.photo_filenames, payload.photo_count)
    bio_strength, headline, bio_rewrite, bio_action = _bio_score_and_rewrite(payload.bio, payload.platform)
    prompt_strength, opener_preview, openers = _prompt_score_and_openers(payload.prompts, payload.bio, payload.platform)
    platform_fit = _platform_fit(payload.platform)

    dq_score = round((photo_quality + bio_strength + prompt_strength + platform_fit) / 4, 1)
    projected_score = round(min(9.1, dq_score + 0.9), 1)

    free_report = FreeReport(
        score=dq_score,
        headline=headline,
        hinge_tip=PLATFORM_TIPS.get(payload.platform.lower(), PLATFORM_TIPS["hinge"]),
        bio_before=payload.bio,
        bio_after_preview=(bio_rewrite[:180] + "…") if len(bio_rewrite) > 180 else bio_rewrite,
        photo_scores_preview=photo_preview,
        openers_preview=opener_preview,
        projected_score=projected_score,
    )

    top_action = (
        "Use your clearest solo photo first, then follow with one social/lifestyle image and one conversation-starter image."
        if payload.photo_count > 0
        else "Add photos before trusting the score. Right now the text is carrying the whole profile."
    )

    pro_report = ProReport(
        looking_for_tags=[LookingForTag(emoji=emoji, label=label) for emoji, label in LOOKING_FOR_MAP],
        target_audience=(
            "This profile will land best with people who like specific plans, playful confidence, and a profile that signals real-world momentum instead of vague vibes."
        ),
        bio_rewrite=bio_rewrite,
        photo_breakdown=photo_breakdown,
        openers=openers,
        projected_score=projected_score,
    )

    notes = [
        "This is the first MVP backend implementation with deterministic scoring and generated structured copy.",
        "Photo analysis is currently metadata-driven; real image understanding can be added later behind the same response schema.",
        bio_action,
        top_action,
    ]

    return AnalysisResponse(
        analysis_id=str(uuid.uuid4()),
        paid=False,
        profile={
            "platform": payload.platform,
            "photo_count": payload.photo_count,
            "prompts_count": len(payload.prompts),
            "source": payload.source,
        },
        free_report=free_report,
        pro_report=pro_report,
        dq_score=dq_score,
        verdict="Promising" if dq_score >= 6.8 else "Needs Work",
        platform=payload.platform,
        breakdown={
            "photo_quality": photo_quality,
            "bio_strength": bio_strength,
            "profile_energy": prompt_strength,
            "platform_fit": platform_fit,
        },
        notes=notes,
    )
