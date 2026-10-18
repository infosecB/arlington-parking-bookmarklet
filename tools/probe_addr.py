"""Read-only: inspect the address combobox's client API and event handlers."""
import json
from playwright.sync_api import sync_playwright
FORM_URL = "https://arlingtonma.mycusthelp.com/WEBAPP/_rs/requestopen.aspx?rqst=71"
A = "requestLocation_RequestLocationFormLayout_txtAddressOneLkup"
with sync_playwright() as p:
    b = p.chromium.launch(headless=True); pg = b.new_page()
    pg.goto(FORM_URL, wait_until="domcontentloaded")
    pg.wait_for_selector("#RequestOpenFormLayout_txtEmail_I", timeout=30000)
    pg.wait_for_timeout(1500)
    print(json.dumps(pg.evaluate("""(A) => {
      const c = ASPxClientControl.GetControlCollection().GetByName(A);
      const names = new Set(); let o = c;
      while (o) { Object.getOwnPropertyNames(o).forEach(n => names.add(n)); o = Object.getPrototypeOf(o); }
      const pick = [...names].filter(n => /filter|callback|select|valuechang|incremental/i.test(n)).sort();
      const ev = {};
      for (const k of ['SelectedIndexChanged','ValueChanged','TextChanged','LostFocus','EndCallback']) {
        const e = c[k]; if (e && e.handlerInfoList) ev[k] = e.handlerInfoList.map(h => String(h.handler).slice(0,400));
      }
      return {pick, ev, filterMinLength: c.filterMinLength, incrementalFilteringMode: c.incrementalFilteringMode};
    }""", A), indent=1))
    b.close()
