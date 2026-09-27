import { useMemo } from "react";
import { useAppStore } from "../store/useAppStore";
import { getCurrentSemesterWeek } from "./useWeekGraph";
import type { Concept, Course } from "../types";

/**
 * Course IDs that make up the "current semester" view. Never returns an empty
 * set when there are concepts to show:
 *   1. Courses whose date window contains now (missing dates count as open-ended),
 *      restricted to courses that actually have concepts.
 *   2. Otherwise, the most recently started term among courses with concepts
 *      (e.g. between semesters, or stale course dates).
 *   3. Otherwise (course IDs don't line up with concept data at all), every
 *      course that has concepts.
 */
export function getSemesterCourseIds(courses: Course[], concepts: Concept[]): Set<string> {
  const conceptCourseIds = new Set(concepts.map((c) => c.course_id));
  const withConcepts = courses.filter((c) => conceptCourseIds.has(c.id));
  const now = Date.now();

  const current = withConcepts.filter((course) => {
    if (course.workflow_state === "completed") return false;
    const start = course.start_at ? Date.parse(course.start_at) : NaN;
    const end = course.end_at ? Date.parse(course.end_at) : NaN;
    return (isNaN(start) || start <= now) && (isNaN(end) || end >= now);
  });
  if (current.length > 0) return new Set(current.map((c) => c.id));

  const started = withConcepts
    .map((c) => ({ id: c.id, start: c.start_at ? Date.parse(c.start_at) : NaN }))
    .filter((c) => !isNaN(c.start) && c.start <= now);
  if (started.length > 0) {
    const latest = Math.max(...started.map((c) => c.start));
    // Same term if it started within ~2 months of the latest start.
    const window = 60 * 24 * 60 * 60 * 1000;
    return new Set(started.filter((c) => latest - c.start <= window).map((c) => c.id));
  }

  return conceptCourseIds;
}

/**
 * Centralized graph filtering pipeline.
 * Reads graphFilters from the store and returns filtered concepts + connections.
 *
 * Pipeline order:
 *   1. courseIds  — keep only selected courses (empty = all)
 *   2. masteryRange — keep concepts whose mastery is within [min, max]
 *   3. viewMode
 *      - "full"     → no additional filtering
 *      - "week"     → intersect with current syllabus week concept IDs
 *      - "overview" → collapse to one synthetic node per course
 */
export function useGraphFilters() {
  const concepts = useAppStore((s) => s.concepts);
  const connections = useAppStore((s) => s.connections);
  const syllabi = useAppStore((s) => s.syllabi);
  const courses = useAppStore((s) => s.courses);
  const graphFilters = useAppStore((s) => s.graphFilters);

  const { courseIds, masteryRange, viewMode } = graphFilters;

  const filtered = useMemo(() => {
    // 1. Course filter
    let fc: Concept[] =
      courseIds.length > 0
        ? concepts.filter((c) => courseIds.includes(c.course_id))
        : concepts;

    // 2. Mastery range filter
    fc = fc.filter(
      (c) => c.mastery >= masteryRange[0] && c.mastery <= masteryRange[1]
    );

    const semesterCourseIds = getSemesterCourseIds(courses, concepts);

    // 3. View mode
    if (viewMode === "semester") {
      fc = fc.filter((c) => semesterCourseIds.has(c.course_id));
    }

    if (viewMode === "week") {
      const currentWeek = getCurrentSemesterWeek();
      const weekIds = new Set<string>();
      syllabi.forEach((syllabus) => {
        // Only pull week concepts for active semester courses
        if (semesterCourseIds.has(syllabus.course_id)) {
          if (courseIds.length === 0 || courseIds.includes(syllabus.course_id)) {
            const week = syllabus.weeks.find((w) => w.week === currentWeek);
            if (week) week.concept_ids.forEach((id) => weekIds.add(id));
          }
        }
      });
      if (weekIds.size > 0) {
        fc = fc.filter((c) => weekIds.has(c.id));
      }
    }



    // Filter connections so both endpoints are in the filtered concept set
    const conceptIds = new Set(fc.map((c) => c.id));
    const fc_conn = connections.filter(
      (conn) => conceptIds.has(conn.source_id) && conceptIds.has(conn.target_id)
    );

    return { concepts: fc, connections: fc_conn };
  }, [concepts, connections, syllabi, courses, courseIds, masteryRange, viewMode]);

  return filtered;
}
