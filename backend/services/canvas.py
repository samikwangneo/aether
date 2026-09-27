"""
Canvas (ELMS) Bridge
=====================
UMD disables Canvas's self-service Personal Access Token generation for students
(API Developer Keys are reserved for vetted LTI vendors / central IT), so the usual
"grab a token, call the REST API with a Bearer header" approach isn't available here.

Instead, this mirrors what Canvas browser extensions do: Canvas's own web frontend
calls the exact same `/api/v1/...` REST API, authenticated by browser session cookie
instead of a token. We use Playwright *once* to drive UMD's CAS+Duo SSO login and
capture that session, then talk to the API directly via httpx -- no browser stays
open for steady-state polling (unlike the old always-open TerpAI Playwright bridge).

FULL FLOW:
    Startup (start())
        -> fast path: load cookies from canvas-session.json, smoke-test, done
        -> slow path (only if fast path fails):
             CANVAS_HEADLESS=true  -> log instructions, stay not-ready (no unattended Duo)
             CANVAS_HEADLESS=false -> launch headed browser, wait for interactive login,
                                       persist session, continue

    Steady state
        get_courses() / get_assignments() / get_announcements()
        -> TTL-cached, backed by plain httpx calls following Canvas's Link-header pagination

This is inherently single-user/local: it only works for whoever completes the
interactive Duo login on this machine. Not meant for the public Railway deployment.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from pathlib import Path

import httpx

from services import canvas_mapper

log = logging.getLogger("canvas")


class CanvasError(Exception):
    """Raised when Canvas access fails. Callers should fall back to mock data."""
    pass


class CanvasLoginRequired(CanvasError):
    """Session missing or expired -- run refresh_canvas_session.py."""
    pass


_LOGIN_PAGE_MARKERS = [
    "login", "signin", "sign-in", "cas.umd.edu", "shib.umd.edu",
    "shib.idm.umd.edu", "shibboleth",
]

_MAX_CONTEXT_CODES_PER_REQUEST = 15


class CanvasBridge:
    """
    Session-cookie bridge to Canvas's REST API.
    Lifecycle managed by FastAPI lifespan (start/stop), same pattern as TerpAIBridge.
    """

    PROFILE_DIR = Path(__file__).parent.parent / ".canvas-profile"
    SESSION_FILE = Path(__file__).parent.parent / "canvas-session.json"

    def __init__(self):
        self._client: httpx.AsyncClient | None = None
        self._base_url: str = ""
        self._ready = False
        self._lock = asyncio.Lock()
        self._cache_ttl = 900.0
        self._cache: dict[str, tuple[float, list[dict]]] = {}
        # normalized course slug (e.g. "cmsc330") -> Canvas's raw numeric course id
        self._course_canvas_ids: dict[str, int] = {}

    @property
    def ready(self) -> bool:
        return self._ready

    # ─── Lifecycle ─────────────────────────────────────────────────────────

    async def start(self):
        """Initialize the bridge. Called at app startup (backgrounded -- must not block)."""
        self._base_url = os.getenv("CANVAS_BASE_URL", "https://elms.umd.edu").rstrip("/")
        self._cache_ttl = float(os.getenv("CANVAS_CACHE_TTL_SECONDS", "900"))
        headless = os.getenv("CANVAS_HEADLESS", "true").strip().lower() != "false"

        log.info("Starting Canvas bridge...")

        # ── Fast path: reuse a previously saved session, no browser involved ──
        if self.SESSION_FILE.exists():
            try:
                await self._build_client_from_session_file()
                if await self._verify_client():
                    log.info("Canvas session restored from canvas-session.json")
                    self._ready = True
                    return
                log.warning("Saved Canvas session is no longer valid (expired?).")
            except Exception as e:
                log.warning(f"Could not restore Canvas session: {e}")
            if self._client:
                await self._client.aclose()
                self._client = None

        # ── Slow path: need a fresh interactive login ──
        if headless:
            log.warning(
                "Canvas not authenticated. Duo MFA can't complete unattended, so run "
                "`python refresh_canvas_session.py` once (headed) and restart the server. "
                "Falling back to mock course data until then."
            )
            self._ready = False
            return

        try:
            await self._login_via_playwright()
            if await self._verify_client():
                self._ready = True
                log.info("Canvas login successful, session saved.")
            else:
                log.error("Canvas login flow completed but the session doesn't look valid.")
                self._ready = False
        except Exception as e:
            log.error(f"Canvas interactive login failed: {e}")
            self._ready = False

    async def stop(self):
        """Close the HTTP client. Called at app shutdown."""
        log.info("Shutting down Canvas bridge...")
        if self._client:
            await self._client.aclose()
            self._client = None
        self._ready = False

    # ─── Session / Cookie Plumbing ─────────────────────────────────────────

    def _cookies_from_storage_state(self, storage_state: dict) -> httpx.Cookies:
        jar = httpx.Cookies()
        for c in storage_state.get("cookies", []):
            jar.set(c["name"], c["value"], domain=c.get("domain", ""), path=c.get("path", "/"))
        return jar

    async def _build_client_from_session_file(self):
        storage_state = json.loads(self.SESSION_FILE.read_text(encoding="utf-8"))
        cookies = self._cookies_from_storage_state(storage_state)
        self._client = httpx.AsyncClient(
            cookies=cookies,
            timeout=httpx.Timeout(30.0, connect=10.0),
            follow_redirects=True,
            headers={"Accept": "application/json"},
        )

    async def _verify_client(self) -> bool:
        """Smoke-test the current client against a real Canvas API call."""
        if not self._client:
            return False
        try:
            resp = await self._client.get(f"{self._base_url}/api/v1/users/self")
            if resp.status_code != 200:
                return False
            content_type = resp.headers.get("content-type", "")
            return "application/json" in content_type
        except Exception as e:
            log.warning(f"Canvas session verification failed: {e}")
            return False

    async def _login_via_playwright(self):
        """Headed interactive login. Only called when CANVAS_HEADLESS=false. Callers
        should prefer running refresh_canvas_session.py directly instead."""
        from playwright.async_api import async_playwright

        login_timeout_ms = int(os.getenv("CANVAS_LOGIN_TIMEOUT_MS", "180000"))
        self.PROFILE_DIR.mkdir(exist_ok=True)

        pw = await async_playwright().start()
        try:
            context = await pw.chromium.launch_persistent_context(
                user_data_dir=str(self.PROFILE_DIR),
                headless=False,
                viewport={"width": 1280, "height": 900},
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            try:
                page = context.pages[0] if context.pages else await context.new_page()
                await page.goto(self._base_url, wait_until="domcontentloaded")

                log.info("Waiting for interactive UMD CAS + Duo login...")
                deadline = time.monotonic() + login_timeout_ms / 1000
                while time.monotonic() < deadline:
                    if not await self._page_looks_like_login(page):
                        break
                    await asyncio.sleep(2)
                else:
                    raise CanvasError("Login timed out")

                await asyncio.sleep(2)  # let post-login redirects settle
                storage_state = await context.storage_state()
                self.SESSION_FILE.write_text(json.dumps(storage_state), encoding="utf-8")

                cookies = self._cookies_from_storage_state(storage_state)
                self._client = httpx.AsyncClient(
                    cookies=cookies,
                    timeout=httpx.Timeout(30.0, connect=10.0),
                    follow_redirects=True,
                    headers={"Accept": "application/json"},
                )
            finally:
                await context.close()
        finally:
            await pw.stop()

    async def _page_looks_like_login(self, page) -> bool:
        try:
            url = page.url.lower()
            title = (await page.title()).lower()
        except Exception:
            await asyncio.sleep(1)
            url = page.url.lower()
            title = (await page.title()).lower()
        return any(marker in url or marker in title for marker in _LOGIN_PAGE_MARKERS)

    def _looks_like_login_response(self, resp: httpx.Response) -> bool:
        if resp.status_code in (401, 403):
            return True
        content_type = resp.headers.get("content-type", "")
        if "text/html" in content_type:
            snippet = resp.text[:1000].lower()
            return any(marker in snippet for marker in _LOGIN_PAGE_MARKERS)
        return False

    def _handle_expired_session(self):
        self._ready = False
        log.warning(
            "Canvas session expired mid-request. Run `python refresh_canvas_session.py` "
            "and restart the server to restore live data. Falling back to mock data."
        )

    # ─── Pagination ─────────────────────────────────────────────────────────

    async def _get_all_pages(self, path: str, params: dict) -> list[dict]:
        if not self._client:
            raise CanvasLoginRequired("Canvas HTTP client not initialized")

        results: list[dict] = []
        url: str | None = f"{self._base_url}{path}"
        request_params: dict | None = {**params, "per_page": params.get("per_page", 100)}

        while url:
            resp = await self._client.get(url, params=request_params)
            if self._looks_like_login_response(resp):
                self._handle_expired_session()
                raise CanvasLoginRequired(f"Canvas session invalid for {path}")
            resp.raise_for_status()
            page_data = resp.json()
            if isinstance(page_data, list):
                results.extend(page_data)
            else:
                results.append(page_data)

            next_link = resp.links.get("next")
            url = next_link["url"] if next_link else None
            request_params = None  # next URL already carries its own query params

        return results

    # ─── Cache helper ────────────────────────────────────────────────────────

    async def _cached(self, key: str, fetch, force_refresh: bool = False) -> list[dict]:
        now = time.monotonic()
        if not force_refresh and key in self._cache:
            ts, data = self._cache[key]
            if now - ts < self._cache_ttl:
                return data
        data = await fetch()
        self._cache[key] = (now, data)
        return data

    # ─── Public Data Accessors ─────────────────────────────────────────────

    async def get_courses(self, force_refresh: bool = False) -> list[dict]:
        if not self._ready:
            raise CanvasLoginRequired("Canvas bridge not ready")
        return await self._cached("courses", self._fetch_courses, force_refresh)

    async def get_assignments(self, force_refresh: bool = False) -> list[dict]:
        if not self._ready:
            raise CanvasLoginRequired("Canvas bridge not ready")
        return await self._cached("assignments", self._fetch_assignments, force_refresh)

    async def get_announcements(self, force_refresh: bool = False) -> list[dict]:
        if not self._ready:
            raise CanvasLoginRequired("Canvas bridge not ready")
        return await self._cached("announcements", self._fetch_announcements, force_refresh)

    # ─── Fetch + Map ─────────────────────────────────────────────────────────

    async def _fetch_custom_colors(self) -> dict[str, str]:
        try:
            resp = await self._client.get(f"{self._base_url}/api/v1/users/self/colors")
            resp.raise_for_status()
            return resp.json().get("custom_colors", {})
        except Exception as e:
            log.debug(f"Could not fetch Canvas custom colors: {e}")
            return {}

    async def _fetch_courses(self) -> list[dict]:
        raw_courses = await self._get_all_pages(
            "/api/v1/courses",
            {"enrollment_state": "active", "include[]": ["teachers", "term"]},
        )
        custom_colors = await self._fetch_custom_colors()

        mapped: list[dict] = []
        self._course_canvas_ids = {}
        for raw in raw_courses:
            course = canvas_mapper.map_course(raw, custom_colors)
            if not course:
                continue
            mapped.append(course)
            self._course_canvas_ids[course["id"]] = raw["id"]

        log.info(f"Fetched {len(mapped)} live Canvas courses")
        return mapped

    async def _fetch_assignment_group_names(self, canvas_course_id: int) -> dict[int, str]:
        try:
            groups = await self._get_all_pages(
                f"/api/v1/courses/{canvas_course_id}/assignment_groups",
                {"include[]": ["assignments"]},
            )
        except CanvasError:
            return {}
        names: dict[int, str] = {}
        for group in groups:
            for a in group.get("assignments", []) or []:
                names[a["id"]] = group.get("name", "")
        return names

    async def _fetch_assignments(self) -> list[dict]:
        if not self._course_canvas_ids:
            await self._fetch_courses()

        mapped: list[dict] = []
        for slug, canvas_id in self._course_canvas_ids.items():
            try:
                raw_assignments = await self._get_all_pages(
                    f"/api/v1/courses/{canvas_id}/assignments",
                    {"include[]": ["submission"], "order_by": "due_at"},
                )
                group_names = await self._fetch_assignment_group_names(canvas_id)
            except CanvasError:
                raise
            except Exception as e:
                log.warning(f"Could not fetch assignments for course {slug}: {e}")
                continue

            for raw in raw_assignments:
                assignment = canvas_mapper.map_assignment(
                    raw, slug, group_name=group_names.get(raw["id"])
                )
                if assignment:
                    mapped.append(assignment)

        log.info(f"Fetched {len(mapped)} live Canvas assignments")
        return mapped

    async def _fetch_announcements(self) -> list[dict]:
        if not self._course_canvas_ids:
            await self._fetch_courses()

        canvas_id_to_slug = {v: k for k, v in self._course_canvas_ids.items()}
        canvas_ids = list(self._course_canvas_ids.values())
        if not canvas_ids:
            return []

        mapped: list[dict] = []
        for i in range(0, len(canvas_ids), _MAX_CONTEXT_CODES_PER_REQUEST):
            chunk = canvas_ids[i : i + _MAX_CONTEXT_CODES_PER_REQUEST]
            context_codes = [f"course_{cid}" for cid in chunk]
            raw_announcements = await self._get_all_pages(
                "/api/v1/announcements",
                {"context_codes[]": context_codes},
            )
            for raw in raw_announcements:
                context_code = raw.get("context_code", "")
                canvas_id = context_code.replace("course_", "")
                try:
                    canvas_id = int(canvas_id)
                except ValueError:
                    continue
                slug = canvas_id_to_slug.get(canvas_id)
                if not slug:
                    continue
                mapped.append(canvas_mapper.map_announcement(raw, slug))

        log.info(f"Fetched {len(mapped)} live Canvas announcements")
        return mapped


# ─── Singleton Instance ────────────────────────────────────────────────────────

bridge = CanvasBridge()
