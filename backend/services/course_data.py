"""
Course Data Accessor
====================
Single seam every router calls through for course/assignment/announcement data,
instead of each independently importing the static mock lists. Tries live Canvas
data first (if the bridge is authenticated), falls back to the mock data used for
demos and for whichever notes/concepts/connections/syllabi have no Canvas equivalent.
"""

import logging

from services.canvas import bridge as canvas_bridge, CanvasError

log = logging.getLogger("course_data")

try:
    from data.courses import COURSES as _MOCK_COURSES
except ImportError:
    _MOCK_COURSES = []

try:
    from data.assignments import ASSIGNMENTS as _MOCK_ASSIGNMENTS
except ImportError:
    _MOCK_ASSIGNMENTS = []

try:
    from data.announcements import ANNOUNCEMENTS as _MOCK_ANNOUNCEMENTS
except ImportError:
    _MOCK_ANNOUNCEMENTS = []

try:
    from data.notes import NOTES as _MOCK_NOTES
except ImportError:
    _MOCK_NOTES = []

try:
    from data.concepts import CONCEPTS as _MOCK_CONCEPTS
except ImportError:
    _MOCK_CONCEPTS = []

try:
    from data.connections import CONNECTIONS as _MOCK_CONNECTIONS
except ImportError:
    _MOCK_CONNECTIONS = []

try:
    from data.syllabus import SYLLABUS as _MOCK_SYLLABUS
except ImportError:
    _MOCK_SYLLABUS = []


async def get_courses() -> list[dict]:
    """Live Canvas courses if authenticated, else the mock roster."""
    if canvas_bridge.ready:
        try:
            live = await canvas_bridge.get_courses()
            if live:
                return live
        except CanvasError as e:
            log.warning(f"Canvas courses fetch failed, using mock data: {e}")
    return _MOCK_COURSES


async def get_assignments() -> list[dict]:
    """Live Canvas assignments if authenticated, else the mock set."""
    if canvas_bridge.ready:
        try:
            live = await canvas_bridge.get_assignments()
            if live:
                return live
        except CanvasError as e:
            log.warning(f"Canvas assignments fetch failed, using mock data: {e}")
    return _MOCK_ASSIGNMENTS


async def get_announcements() -> list[dict]:
    """Live Canvas announcements if authenticated, else the mock set."""
    if canvas_bridge.ready:
        try:
            return await canvas_bridge.get_announcements()
        except CanvasError as e:
            log.warning(f"Canvas announcements fetch failed, using mock data: {e}")
    return _MOCK_ANNOUNCEMENTS


# Notes/concepts/connections/syllabi have no Canvas equivalent -- always mock.

def get_notes() -> list[dict]:
    return _MOCK_NOTES


def get_concepts() -> list[dict]:
    return _MOCK_CONCEPTS


def get_connections() -> list[dict]:
    return _MOCK_CONNECTIONS


def get_syllabi() -> list[dict]:
    return _MOCK_SYLLABUS
