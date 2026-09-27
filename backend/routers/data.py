"""
Data router — serves course data to the frontend.
Live Canvas data when the bridge is authenticated, mock data otherwise
(see services/course_data.py for the fallback logic).

GET /api/courses
GET /api/assignments
GET /api/notes
GET /api/concepts
GET /api/connections
GET /api/syllabi
GET /api/announcements
"""

from fastapi import APIRouter

from services import course_data

router = APIRouter()


@router.get("/courses")
async def get_courses():
    """Return all enrolled courses."""
    return await course_data.get_courses()


@router.get("/assignments")
async def get_assignments():
    """Return all assignments and exams."""
    return await course_data.get_assignments()


@router.get("/notes")
async def get_notes():
    """Return all lecture notes."""
    return course_data.get_notes()


@router.get("/concepts")
async def get_concepts():
    """Return all knowledge graph concept nodes."""
    return course_data.get_concepts()


@router.get("/connections")
async def get_connections():
    """Return all knowledge graph edges."""
    return course_data.get_connections()


@router.get("/syllabi")
async def get_syllabi():
    """Return syllabi for all courses."""
    return course_data.get_syllabi()


@router.get("/announcements")
async def get_announcements():
    """Return all course announcements."""
    return await course_data.get_announcements()
