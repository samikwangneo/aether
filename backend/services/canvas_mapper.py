"""
Canvas Mapper
=============
Pure functions that translate raw Canvas LMS REST API JSON into the shapes
defined in `models.data_models` (CourseModel / AssignmentModel / AnnouncementModel).

No I/O happens here -- `services/canvas.py` fetches the raw JSON (including any
extra lookups like assignment_groups or custom colors) and passes it in.

Canvas has no equivalent for a handful of Aether-specific UI fields (credits,
progress, color, assignment_category, status, priority). Those are derived with
simple heuristics, called out below -- good enough for a dashboard, not a
considered product decision.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

# Canvas submission_types that map directly onto AssignmentModel's Literal.
# Anything else (external_tool, online_url, media_recording, student_annotation,
# not_graded, ...) has no slot in the model and is dropped.
_KNOWN_SUBMISSION_TYPES = {
    "online_upload",
    "online_text_entry",
    "online_quiz",
    "on_paper",
    "discussion_topic",
    "none",
}

_COLOR_PALETTE = [
    "#8B5CF6", "#3B82F6", "#06B6D4", "#F43F5E", "#10B981",
    "#F59E0B", "#EC4899", "#6366F1", "#84CC16", "#14B8A6",
]

_EXAM_PATTERN = re.compile(r"\b(midterm|final|exam)\b", re.IGNORECASE)
_PROJECT_PATTERN = re.compile(r"\bproject\b", re.IGNORECASE)
_QUIZ_PATTERN = re.compile(r"\bquiz\b", re.IGNORECASE)
_LAB_PATTERN = re.compile(r"\blab\b", re.IGNORECASE)
_COURSE_CODE_PATTERN = re.compile(r"^\s*([A-Za-z]{3,4})\s*-?\s*(\d{3}[A-Za-z]?)(?!\d)")


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def derive_course_id(raw_course: dict) -> str:
    """Slugify course_code (e.g. 'CMSC330') rather than using Canvas's raw numeric id,
    so any overlapping mock notes/concepts/syllabi stay keyed correctly."""
    code = raw_course.get("course_code") or raw_course.get("name") or str(raw_course.get("id", ""))
    # Canvas course codes often carry section/term suffixes ("CMSC330-0101",
    # "CMSC330 (Fall 2026)"); key on the bare subject+number so they line up
    # with the concept/syllabus data.
    m = _COURSE_CODE_PATTERN.match(code)
    if m:
        return (m.group(1) + m.group(2)).lower()
    slug = re.sub(r"[^a-z0-9]+", "", code.lower())
    return slug or str(raw_course["id"])


def _derive_color(course_id: str, custom_colors: dict[str, str] | None, canvas_id: int | str) -> str:
    if custom_colors:
        real = custom_colors.get(f"course_{canvas_id}")
        if real:
            return real
    # Deterministic fallback so the same course always gets the same color.
    idx = sum(ord(c) for c in course_id) % len(_COLOR_PALETTE)
    return _COLOR_PALETTE[idx]


def _derive_progress(start_at: str | None, end_at: str | None) -> int:
    start = _parse_iso(start_at)
    end = _parse_iso(end_at)
    if not start or not end or end <= start:
        return 0
    now = datetime.now(timezone.utc)
    fraction = (now - start).total_seconds() / (end - start).total_seconds()
    return max(0, min(100, round(fraction * 100)))


def map_course(
    raw: dict,
    custom_colors: dict[str, str] | None = None,
    credits_default: int = 3,
) -> dict | None:
    """Map a raw `GET /api/v1/courses` entry to a CourseModel-shaped dict.
    Returns None for entries that clearly aren't real enrolled courses."""
    if raw.get("access_restricted_by_date") or not raw.get("name"):
        return None

    course_id = derive_course_id(raw)
    term = raw.get("term") or {}
    start_at = raw.get("start_at") or term.get("start_at")
    end_at = raw.get("end_at") or term.get("end_at")

    teachers = raw.get("teachers") or []
    instructor = teachers[0]["display_name"] if teachers else "Staff"

    return {
        "id": course_id,
        "course_code": raw.get("course_code", raw.get("name", course_id.upper())),
        "name": raw.get("name", course_id.upper()),
        "workflow_state": raw.get("workflow_state", "available"),
        "start_at": start_at,
        "end_at": end_at,
        "created_at": raw.get("created_at"),
        "time_zone": raw.get("time_zone", "America/New_York"),
        "color": _derive_color(course_id, custom_colors, raw["id"]),
        "instructor": instructor,
        "credits": credits_default,
        "progress": _derive_progress(start_at, end_at),
    }


def _map_submission_types(raw_types: list[str] | None) -> list[str]:
    mapped = [t for t in (raw_types or []) if t in _KNOWN_SUBMISSION_TYPES]
    return mapped or ["none"]


def _derive_assignment_category(name: str, submission_types: list[str], group_name: str | None) -> str:
    if group_name:
        g = group_name.lower()
        if "exam" in g or "midterm" in g or "final" in g:
            return "exam"
        if "quiz" in g:
            return "quiz"
        if "project" in g:
            return "project"
        if "lab" in g:
            return "lab"
        if "homework" in g or "assignment" in g:
            return "homework"

    if _EXAM_PATTERN.search(name):
        return "exam"
    if _PROJECT_PATTERN.search(name):
        return "project"
    if _LAB_PATTERN.search(name):
        return "lab"
    if _QUIZ_PATTERN.search(name) or "online_quiz" in submission_types:
        return "quiz"
    return "homework"


def _derive_status(raw: dict, due: datetime | None) -> str:
    submission = raw.get("submission") or {}
    sub_state = submission.get("workflow_state")
    if sub_state == "graded" or submission.get("score") is not None:
        return "graded"
    if sub_state == "submitted" or submission.get("submitted_at") or raw.get("has_submitted_submissions"):
        return "submitted"
    if due and due < datetime.now(timezone.utc):
        return "in_progress"
    return "upcoming"


def _derive_priority(category: str, due: datetime | None) -> str:
    priority = "medium"
    if category in ("exam", "project"):
        priority = "high"
    if due:
        hours_until_due = (due - datetime.now(timezone.utc)).total_seconds() / 3600
        if 0 <= hours_until_due <= 48:
            priority = "critical" if priority == "high" else "high"
    return priority


def map_assignment(raw: dict, course_id: str, group_name: str | None = None) -> dict | None:
    """Map a raw `GET /api/v1/courses/:id/assignments` entry to an AssignmentModel-shaped
    dict. Returns None for assignments with no due date -- the model requires one, and
    an unscheduled assignment (draft/placeholder) isn't useful on the dashboard anyway."""
    due_at = raw.get("due_at")
    due = _parse_iso(due_at)
    if not due_at or not due:
        return None

    name = raw.get("name", "Untitled Assignment")
    submission_types = _map_submission_types(raw.get("submission_types"))
    category = _derive_assignment_category(name, submission_types, group_name)

    return {
        "id": str(raw["id"]),
        "course_id": course_id,
        "name": name,
        "submission_types": submission_types,
        "assignment_category": category,
        "due_at": due_at,
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
        "has_submitted_submissions": bool(raw.get("has_submitted_submissions")),
        "points_possible": raw.get("points_possible") or 0,
        "workflow_state": raw.get("workflow_state", "published"),
        "description": raw.get("description"),
        "status": _derive_status(raw, due),
        "priority": _derive_priority(category, due),
    }


def map_announcement(raw: dict, course_id: str) -> dict:
    """Map a raw `GET /api/v1/announcements` entry to an AnnouncementModel-shaped dict."""
    author = raw.get("author") or {}
    return {
        "id": str(raw["id"]),
        "course_id": course_id,
        "title": raw.get("title", "Announcement"),
        "message": raw.get("message", ""),
        "author": author.get("display_name", "Instructor"),
        "posted_at": raw.get("posted_at") or raw.get("created_at") or datetime.now(timezone.utc).isoformat(),
        "read_state": raw.get("read_state", "unread"),
        "pinned": bool(raw.get("locked", False)),
        "importance": "medium",
    }
