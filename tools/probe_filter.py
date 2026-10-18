"""Read-only: try ways to trigger address filtering from script."""
import json
from playwright.sync_api import sync_playwright
FORM_URL = "https://arlingtonma.mycusthelp.com/WEBAPP/_rs/requestopen.aspx?rqst=71"
A = "requestLocation_RequestLocationFormLayout_txtAddressOneLkup"
with sync_playwright() as p:
    b = p.chromium.launch(headless=True); pg = b.new_page()
    pg.goto(FORM_URL, wait_until="domcontentloaded")
    pg.wait_for_selector("#RequestOpenFormLayout_txtEmail_I", timeout=30000)
    pg.wait_for_timeout(1500)
    print(pg.evaluate("""(A) => {
      const c = ASPxClientControl.GetControlCollection().GetByName(A);
      const fs = c.filterStrategy; const names = new Set(); let o = fs;
      while (o) { Object.getOwnPropertyNames(o).forEach(n => names.add(n)); o = Object.getPrototypeOf(o); }
      return [...names].filter(n => /filter|key|input|text/i.test(n)).sort().join(' ');
    }""", A))
    # Attempt: set input value and dispatch keyup
    pg.evaluate("""(A) => {
      const inp = document.getElementById(A + '_I');
      inp.focus(); inp.value = '12 MASS';
      inp.dispatchEvent(new Event('input', {bubbles:true}));
      inp.dispatchEvent(new KeyboardEvent('keydown', {key:'S', keyCode:83, bubbles:true}));
      inp.dispatchEvent(new KeyboardEvent('keyup', {key:'S', keyCode:83, bubbles:true}));
    }""", A)
    pg.wait_for_timeout(4000)
    print(json.dumps(pg.evaluate("""(A) => {
      const c = ASPxClientControl.GetControlCollection().GetByName(A);
      const r = []; for (let i=0;i<c.GetItemCount();i++) r.push(c.GetItem(i).text); return r.slice(0,12);
    }""", A)))
    b.close()
