"""
Course Recommendation Prompts
=============================
Two prompts that mirror the topic_knowledge.py pattern:

1. build_course_recommendation_prompt  → fed to Gemini's build_knowledge_document
   to create a rich context doc for the TerpAI agent.
2. build_recommendation_json_prompt    → fed to Gemini's generate_json_fallback
   to extract 3 structured course recommendations as JSON.
"""


def build_course_recommendation_prompt(
    taken_courses: list[dict],
    all_cmsc_courses: list[dict],
) -> str:
    """
    Build a Gemini prompt that generates a knowledge document about
    CMSC course offerings, focused on recommending next courses for
    a student who has already taken/is taking `taken_courses`.
    """

    taken_block = "\n".join(
        f"- {c.get('course_id', 'N/A')}: {c.get('name', 'N/A')} — {c.get('description', '')[:200]}"
        for c in taken_courses
    ) or "No taken courses provided."

    catalog_block = "\n".join(
        f"- {c.get('course_id', 'N/A')}: {c.get('name', 'N/A')} "
        f"({c.get('credits', '?')} cr) — {c.get('description', '')[:200]}"
        for c in all_cmsc_courses
    ) or "No catalog data available."

    return f"""You are building a COURSE RECOMMENDATION KNOWLEDGE DOCUMENT for an AI study assistant.

The student is currently taking or has completed these courses:

## Student's Current / Completed Courses
{taken_block}

## Full CMSC Course Catalog at UMD
{catalog_block}

## Your Task
Create a comprehensive knowledge document that:

1. **Student Profile** — Summarize what the student already knows based on their taken courses
2. **Available Next Courses** — List CMSC courses the student has NOT taken that they are eligible for
3. **Recommendation Analysis** — For each potential next course, explain:
   - How it builds on the student's existing knowledge
   - What new skills/topics it covers
   - Career/academic relevance
4. **Top 3 Recommendations** — The 3 most valuable next courses for this student, with detailed rationale

Write as a knowledge base document, NOT a chat response.
This document will be uploaded as context for an AI agent that advises on course selection."""


def build_recommendation_json_prompt(
    context_doc: str,
    taken_course_ids: list[str],
) -> str:
    """
    Build a prompt for generate_json_fallback that extracts exactly
    3 recommended courses as structured JSON from the knowledge doc.
    """
    taken_str = ", ".join(taken_course_ids)

    return f"""Based on the following course recommendation analysis, return EXACTLY 3 recommended
next courses for a student who has taken: {taken_str}.

{context_doc}

Return a JSON array with exactly 3 objects. Each object must have:
- "course_id": the UMD course ID (e.g. "CMSC435")
- "name": the full course name
- "reason": a 1-2 sentence explanation of why this course is recommended

Example format:
[
  {{"course_id": "CMSC435", "name": "Software Engineering", "reason": "Builds directly on..."}},
  {{"course_id": "CMSC451", "name": "Design and Analysis of Algorithms", "reason": "Extends..."}},
  {{"course_id": "CMSC433", "name": "Programming Language Technologies", "reason": "Complements..."}}
]

Return ONLY the JSON array. No markdown, no explanation."""
