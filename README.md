# Arlington overnight parking waiver: one-tap bookmarklet

A setup page where neighbors enter their details once and get a browser
bookmark ("bookmarklet") that fills in the Town of Arlington's
[Overnight Parking Request form](https://arlingtonma.mycusthelp.com/WEBAPP/_rs/requestopen.aspx?rqst=71).
They review the form and press Submit themselves. The bookmarklet never submits.

No server: details are kept in the neighbor's browser (`localStorage`) and baked
into their own bookmark. Nothing is sent anywhere except the town's form.

## Layout

| path | what |
|------|------|
| `src/fill.js` | The bookmarklet. Runs on the town's page and uses its DevExpress client API (`ASPxClientControl`) to set each field. `__CFG__` is replaced with the neighbor's details. |
| `site/index.template.html` | Setup page template (form + install instructions for desktop, iOS, Android). |
| `build.py` | Strips comments from `fill.js`, embeds it into the template, writes `docs/index.html`. |
| `docs/index.html` | Built page. Static, so it can be hosted anywhere (e.g. GitHub Pages from `/docs`). |
| `tools/` | Playwright checks against the live form (they never submit). They use the Playwright venv from `~/arlington-parking-waiver`. |

## Build

```bash
python3 build.py
```

## Test (live form, never submits)

```bash
PY=~/arlington-parking-waiver/.venv/bin/python
$PY tools/e2e.py        # setup page -> bookmarklet -> town form, saves screenshots in tools/
$PY tools/compare.py    # diff form data: bookmarklet vs. Playwright typing (old submit.py)
$PY tools/probe_client_api.py   # list the form's controls/options if the town changes it
```

## How the tricky parts work

- **Address** is a server-filtered lookup. The bookmarklet puts the text in the
  box and calls the control's own `filterStrategy.OnInput()`, which sends the
  same request as typing. It picks the exact match. Failing that, it retries
  with the house number plus the first street word ("12 Pleasant Street" →
  "12 PLEASANT") and takes the result only if that leaves a single address.
  Otherwise it leaves the list open for the person to pick. Selecting an
  address runs the page's own handler, which fills in Address 2, city, and ZIP.
- **Date**: the town wants the "actual" date of the 1–7 a.m. window, so
  "tonight" means tomorrow's date (or today's if it's already past midnight
  and before 7 a.m.). The banner can switch to tomorrow night.
