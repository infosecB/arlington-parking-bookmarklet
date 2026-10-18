"""Read-only: compare real typing vs script; capture callback traffic."""
import json
from playwright.sync_api import sync_playwright
FORM_URL = "https://arlingtonma.mycusthelp.com/WEBAPP/_rs/requestopen.aspx?rqst=71"
A = "requestLocation_RequestLocationFormLayout_txtAddressOneLkup"
LIST = """(A) => { const c = ASPxClientControl.GetControlCollection().GetByName(A);
  const r = []; for (let i=0;i<c.GetItemCount();i++) r.push(c.GetItem(i).text); return r.slice(0,8); }"""
def page(b):
    pg = b.new_page()
    pg.on("request", lambda r: r.method == "POST" and print("   POST", (r.post_data or "")[-160:].replace("\n"," ")))
    pg.goto(FORM_URL, wait_until="domcontentloaded")
    pg.wait_for_selector("#RequestOpenFormLayout_txtEmail_I", timeout=30000)
    pg.wait_for_timeout(1500); return pg
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    pg = page(b); print("real typing:")
    pg.locator(f"#{A}_I").click(); pg.locator(f"#{A}_I").type("12 MASS", delay=90)
    pg.wait_for_timeout(5000); print("  ", json.dumps(pg.evaluate(LIST, A))); pg.close()
    pg = page(b); print("script: SetText-less input + OnInput + timer:")
    print(pg.evaluate("""(A) => { try { const c = ASPxClientControl.GetControlCollection().GetByName(A);
      const inp = c.GetInputElement(); inp.focus(); inp.value = '12 MASS';
      c.filterStrategy.OnInput(); return 'ok' } catch(e) { return String(e) } }""", A))
    pg.wait_for_timeout(5000); print("  ", json.dumps(pg.evaluate(LIST, A))); pg.close()
    b.close()
