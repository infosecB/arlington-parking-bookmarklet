#!/usr/bin/env python3
"""Build docs/index.html (the setup page) from site/index.template.html and src/fill.js."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
FORM_URL = "https://arlingtonma.mycusthelp.com/WEBAPP/_rs/requestopen.aspx?rqst=71"


def compact(js: str) -> str:
    """Shrink the bookmarklet: drop comments and indentation, keep line breaks."""
    js = re.sub(r"/\*.*?\*/", "", js, flags=re.S)
    lines = (ln.strip() for ln in js.splitlines())
    return "\n".join(ln for ln in lines if ln and not ln.startswith("//"))


def main():
    fill = compact((ROOT / "src" / "fill.js").read_text())
    assert "__CFG__" in fill
    html = (ROOT / "site" / "index.template.html").read_text()
    html = html.replace("__FILL_SRC__", json.dumps(fill).replace("</", "<\\/"))
    html = html.replace("__FORM_URL__", FORM_URL)
    out = ROOT / "docs" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html)
    print(f"wrote {out.relative_to(ROOT)} (bookmarklet source {len(fill)} chars)")


if __name__ == "__main__":
    main()
