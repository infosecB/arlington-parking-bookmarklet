"""Fill the live form two ways — Playwright typing (old submit.py helpers) and
the bookmarklet — and diff the form data each would POST. Never submits."""
import json, sys, datetime as dt
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path.home() / "arlington-parking-waiver"))
from submit import FORM_URL, IDS, fill_text, select_combo, parse_date  # noqa

CFG = {"email": "test@example.com", "address": "1 Arnold Street", "unit": "",
       "plate": "test123", "plateState": "MA", "phone": "(781) 555-0100",
       "reason": "Guest Visiting"}
SRC = (Path(__file__).parent.parent / "src" / "fill.js").read_text()
SKIP = ("__VIEWSTATE", "__EVENTVALIDATION", "__REQUESTDIGEST", "__RequestVerificationToken", "DXScript", "DXCss", "DXMVCEditorsValues")
DUMP = """() => { const f = document.forms[0]; const o = {};
  for (const [k, v] of new FormData(f)) o[k] = String(v); return o; }"""

def open_form(b):
    pg = b.new_page(); pg.set_default_timeout(30000)
    pg.on("pageerror", lambda e: print("   pageerror:", e))
    pg.goto(FORM_URL, wait_until="domcontentloaded")
    pg.wait_for_selector(f"#{IDS['email']}"); pg.wait_for_timeout(1500); return pg

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    # A: reference fill via real typing
    a = open_form(b)
    fill_text(a, IDS["email"], CFG["email"])
    select_combo(a, IDS["addr1"], "1 ARNOLD ST", typeahead=True)
    fill_text(a, IDS["carreg"], "TEST123")
    select_combo(a, IDS["regstate"], "MA")
    fill_text(a, IDS["phone"], CFG["phone"])
    select_combo(a, IDS["reason"], "Guest Visiting")
    di = a.locator(f"#{IDS['date']}"); di.click()
    for _ in range(12): di.press("Backspace")
    di.type(parse_date("tonight"), delay=70); a.keyboard.press("Tab"); a.wait_for_timeout(800)
    A = a.evaluate(DUMP)
    # B: bookmarklet
    bk = open_form(b)
    bk.evaluate(SRC.replace("__CFG__", json.dumps(CFG)))
    bk.wait_for_function("() => /filled|Almost/.test((document.getElementById('apw-banner')||{}).innerText||'')", timeout=20000)
    print("banner:", bk.inner_text("#apw-banner").replace("\n", " | "))
    bk.wait_for_timeout(800)
    B = bk.evaluate(DUMP)
    bk.screenshot(path=str(Path(__file__).parent / "bookmarklet_filled.png"), full_page=True)
    b.close()

diff = 0
for k in sorted(set(A) | set(B)):
    if k.startswith(SKIP) or k.endswith(("$State", "_State")) and False: continue
    if A.get(k) != B.get(k):
        diff += 1; print(f"DIFF {k}\n   typed: {A.get(k)!r}\n   bkmk : {B.get(k)!r}")
print(f"{diff} differing fields out of {len(set(A)|set(B))}")
