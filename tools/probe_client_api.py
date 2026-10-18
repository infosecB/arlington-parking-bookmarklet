"""Read-only: list DevExpress client controls on the waiver form and their options."""
import json, sys
from playwright.sync_api import sync_playwright

FORM_URL = "https://arlingtonma.mycusthelp.com/WEBAPP/_rs/requestopen.aspx?rqst=71"
JS = r"""
() => {
  const out = [];
  const coll = window.ASPxClientControl && ASPxClientControl.GetControlCollection();
  if (!coll) return {error: 'no ASPxClientControl'};
  coll.ForEachControl(c => {
    const name = c.name || '';
    if (!/RequestOpenFormLayout|requestLocation|requestData|btnSaveData/.test(name)) return;
    const o = {name, type: c.constructor && c.constructor.name,
               hasSetValue: typeof c.SetValue === 'function',
               hasSetText: typeof c.SetText === 'function',
               hasSetDate: typeof c.SetDate === 'function',
               value: c.GetValue ? String(c.GetValue()) : undefined};
    if (typeof c.GetItemCount === 'function') {
      o.itemCount = c.GetItemCount();
      o.items = [];
      for (let i = 0; i < Math.min(o.itemCount, 80); i++) {
        const it = c.GetItem(i); o.items.push([it.text, it.value]);
      }
      o.callbackMode = !!c.isCallbackMode;
    }
    out.push(o);
  });
  return out;
}
"""
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    pg = b.new_page()
    pg.goto(FORM_URL, wait_until="domcontentloaded")
    pg.wait_for_selector("#RequestOpenFormLayout_txtEmail_I", timeout=30000)
    pg.wait_for_timeout(1500)
    print(json.dumps(pg.evaluate(JS), indent=1))
    b.close()
