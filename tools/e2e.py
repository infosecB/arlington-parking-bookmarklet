"""End-to-end: setup page -> generated bookmarklet -> live town form. Never submits."""
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE = Path(__file__).parent; ROOT = HERE.parent
FORM_URL = "https://arlingtonma.mycusthelp.com/WEBAPP/_rs/requestopen.aspx?rqst=71"
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True,
                        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
    s = ctx.new_page(); errs = []
    s.on("pageerror", lambda e: errs.append(str(e)))
    s.goto((ROOT / "docs" / "index.html").as_uri())
    s.screenshot(path=str(HERE / "setup_empty.png"), full_page=True)
    s.fill("#email", "test@example.com"); s.fill("#address", "1 Arnold St")
    s.fill("#plate", "test 123"); s.fill("#phone", "(781) 555-0100")
    s.click("button[type=submit]"); s.wait_for_timeout(600)
    print("tab shown:", s.eval_on_selector("[data-panel=ios]", "e => !e.hidden"))
    s.screenshot(path=str(HERE / "setup_done.png"), full_page=True)
    href = s.get_attribute("#bm", "href")
    print("bookmarklet length:", len(href), "| page errors:", errs)
    # reload: details persist
    s.reload(); print("persisted plate:", s.input_value("#plate"))
    # run bookmarklet on a non-form page -> confirm dialog
    s.on("dialog", lambda d: (print("dialog on wrong page:", d.message.splitlines()[0]), d.dismiss()))
    s.evaluate("src => eval(decodeURIComponent(src.slice(11)))", href)
    # run on the town form
    t = ctx.new_page(); t.on("pageerror", lambda e: print("   town pageerror:", e))
    t.goto(FORM_URL, wait_until="domcontentloaded"); t.wait_for_selector("#RequestOpenFormLayout_txtEmail_I", timeout=30000)
    t.wait_for_timeout(1500)
    t.evaluate("src => eval(decodeURIComponent(src.slice(11)))", href)
    t.wait_for_function("() => /filled|Almost/.test((document.getElementById('apw-banner')||{}).innerText||'')", timeout=25000)
    print("banner:", t.inner_text("#apw-banner").replace("\n", " | "))
    t.click("#apw-t"); print("after toggle:", t.inner_text("#apw-banner").split("\n")[-1],
          "| field:", t.input_value("#requestData_CustomFieldsFormLayout_cf_119_I"))
    vals = t.evaluate("""() => ['RequestOpenFormLayout_txtEmail_I','requestLocation_RequestLocationFormLayout_txtAddressOneLkup_I',
      'requestLocation_RequestLocationFormLayout_txtZip_I','requestData_CustomFieldsFormLayout_cf_116_I',
      'requestData_CustomFieldsFormLayout_cf_121_I','requestData_CustomFieldsFormLayout_cf_54_I',
      'requestData_CustomFieldsFormLayout_cf_118_I'].map(i => document.getElementById(i).value)""")
    print("town form values:", vals)
    t.screenshot(path=str(HERE / "town_mobile.png"))
    b.close()
