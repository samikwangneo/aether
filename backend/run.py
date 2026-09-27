"""
Launch script for Aether backend.
"""

import asyncio
import os
import sys
import uvicorn

# Playwright (used by the Canvas login bridge) launches Chromium as a subprocess,
# which requires the Proactor event loop on Windows -- the default Selector loop
# raises NotImplementedError on subprocess creation.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
