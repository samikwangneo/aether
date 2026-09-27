"""
Canvas Session Refresher
========================
Run this ONCE (whenever your session expires) to log into ELMS-Canvas and
persist the authenticated session for the server to reuse headlessly.

Usage:
    python refresh_canvas_session.py

What it does:
    1. Opens a visible Chromium browser
    2. Navigates to CANVAS_BASE_URL (default https://elms.umd.edu)
    3. Waits for you to log in via UMD CAS + Duo MFA
    4. Saves the authenticated session to canvas-session.json

After running this, start the server with CANVAS_HEADLESS=true (the default)
and it will read canvas-session.json instead of needing to log in again.
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

CANVAS_BASE_URL = os.getenv("CANVAS_BASE_URL", "https://elms.umd.edu").rstrip("/")
PROFILE_DIR = Path(__file__).parent / ".canvas-profile"
SESSION_FILE = Path(__file__).parent / "canvas-session.json"
LOGIN_TIMEOUT_S = int(os.getenv("CANVAS_LOGIN_TIMEOUT_MS", "180000")) / 1000

_LOGIN_PAGE_MARKERS = [
    "login", "signin", "sign-in", "cas.umd.edu", "shib.umd.edu",
    "shib.idm.umd.edu", "shibboleth",
]


async def _looks_like_login(page) -> bool:
    try:
        url = page.url.lower()
        title = (await page.title()).lower()
    except Exception:
        await asyncio.sleep(1)
        url = page.url.lower()
        title = (await page.title()).lower()
    return any(marker in url or marker in title for marker in _LOGIN_PAGE_MARKERS)


async def main():
    print(f"Opening {CANVAS_BASE_URL} ...")
    print("Log in with UMD CAS + approve the Duo MFA push.")
    print(f"Browser profile: {PROFILE_DIR}")
    print()

    PROFILE_DIR.mkdir(exist_ok=True)

    pw = await async_playwright().start()
    context = await pw.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR),
        headless=False,
        viewport={"width": 1280, "height": 900},
        args=["--no-sandbox", "--disable-dev-shm-usage"],
    )

    page = context.pages[0] if context.pages else await context.new_page()
    await page.goto(CANVAS_BASE_URL, wait_until="domcontentloaded")

    print("Waiting for you to complete login...")

    deadline = time.monotonic() + LOGIN_TIMEOUT_S
    logged_in = False
    while time.monotonic() < deadline:
        if not await _looks_like_login(page):
            logged_in = True
            break
        await asyncio.sleep(2)

    if not logged_in:
        print(f"Login timed out after {int(LOGIN_TIMEOUT_S)}s. Run this script again.")
        await context.close()
        await pw.stop()
        return

    await asyncio.sleep(3)  # let post-login redirects settle

    storage_state = await context.storage_state()
    SESSION_FILE.write_text(json.dumps(storage_state), encoding="utf-8")

    print(f"\nLogin successful! Session saved to {SESSION_FILE.name}")
    print("You can now start the server with CANVAS_HEADLESS=true")
    print("and it will skip the login screen entirely.\n")

    await context.close()
    await pw.stop()


if __name__ == "__main__":
    asyncio.run(main())
