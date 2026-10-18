"""Read-only: try filterStrategy entry points for address filtering."""
import json
from playwright.sync_api import sync_playwright
FORM_URL = "https://arlingtonma.mycusthelp.com/WEBAPP/_rs/requestopen.aspx?rqst=71"
A = "requestLocation_RequestLocationFormLayout_txtAddressOneLkup"
LIST = """(A) => { const c = ASPxClientControl.GetControlCollection().GetByName(A);
  const r = []; for (let i=0;i<c.GetItemCount();i++) r.push(c.GetItem(i).text); return r.slice(0,8); }"""
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    for method in ["Filtering", "FilterNowAndApply", "FilterStartTimer"]:
        pg = b.new_page()
        pg.goto(FORM_URL, wait_until="domcontentloaded")
        pg.wait_for_selector("#RequestOpenFormLayout_txtEmail_I", timeout=30000)
        pg.wait_for_timeout(1500)
        err = pg.evaluate("""([A, m]) => { try {
          const c = ASPxClientControl.GetControlCollection().GetByName(A);
          const inp = c.GetInputElement(); inp.focus(); inp.value = '12 MASS';
          c.filterStrategy[m](); return 'ok'; } catch (e) { return String(e); } }""", [A, method])
        pg.wait_for_timeout(4000)
        print(method, err, json.dumps(pg.evaluate(LIST, A)))
        pg.close()
    b.close()
