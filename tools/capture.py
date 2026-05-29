"""
capture.py

Boot Playwright + Chromium with WebGL enabled, navigate to the local Astro
dev server, optionally scroll to a specific section, wait for the 3D scene
to settle (preloader to fade out), and write a screenshot to disk.

Usage:
    python3 tools/capture.py <out.png> [section_id] [extra_wait_ms]
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


URL = "http://127.0.0.1:4321/"
VIEWPORT = {"width": 1600, "height": 1000}


def main() -> None:
    args = sys.argv[1:]
    out_path = Path(args[0]) if args else Path("tools/screenshots/capture.png")
    section_id = args[1] if len(args) > 1 and args[1] else ""
    extra_wait_ms = int(args[2]) if len(args) > 2 and args[2] else 4000

    out_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--use-angle=swiftshader",
                "--enable-webgl",
                "--ignore-gpu-blocklist",
                "--disable-web-security",
            ],
        )
        ctx = browser.new_context(viewport=VIEWPORT, device_scale_factor=1)
        page = ctx.new_page()

        console_log: list[str] = []
        page.on("console", lambda msg: console_log.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: console_log.append(f"[error] {err}"))

        page.goto(URL, wait_until="domcontentloaded", timeout=60000)

        try:
            page.wait_for_function(
                """() => {
                    const pre = document.getElementById('preloader');
                    if (!pre) return true;
                    const style = window.getComputedStyle(pre);
                    if (style.display === 'none') return true;
                    if (parseFloat(style.opacity) < 0.05) return true;
                    if (pre.classList.contains('is-hidden') ||
                        pre.classList.contains('hidden') ||
                        pre.classList.contains('done') ||
                        pre.classList.contains('complete')) return true;
                    return false;
                }""",
                timeout=45000,
            )
            print("preloader dismissed")
        except Exception as e:
            print(f"preloader wait timed out: {e}")

        page.wait_for_timeout(2000)

        if section_id:
            page.evaluate(
                "(id) => { const el = document.getElementById(id);"
                "if (el) el.scrollIntoView({behavior:'instant', block:'start'}); }",
                section_id,
            )
            page.wait_for_timeout(extra_wait_ms)
        else:
            page.wait_for_timeout(extra_wait_ms)

        page.screenshot(path=str(out_path), full_page=False)
        browser.close()

    log_path = out_path.with_suffix(".log.txt")
    log_path.write_text("\n".join(console_log))
    print(f"wrote {out_path}")
    print(f"console log -> {log_path} ({len(console_log)} lines)")


if __name__ == "__main__":
    main()
