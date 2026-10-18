/*
 * Fills the Town of Arlington "Overnight Parking Request" form
 * (https://arlingtonma.mycusthelp.com/WEBAPP/_rs/requestopen.aspx?rqst=71)
 * using the page's own DevExpress client API. It never clicks Submit.
 *
 * The setup page replaces __CFG__ with the neighbor's saved details and turns
 * this file into a javascript: bookmarklet.
 */
(function (cfg) {
  var FORM_URL = "https://arlingtonma.mycusthelp.com/WEBAPP/_rs/requestopen.aspx?rqst=71";
  var N = {
    email:    "RequestOpenFormLayout_txtEmail",
    addr1:    "requestLocation_RequestLocationFormLayout_txtAddressOneLkup",
    addr2:    "requestLocation_RequestLocationFormLayout_txtAddressTwo",
    unit:     "requestData_CustomFieldsFormLayout_cf_44",
    plate:    "requestData_CustomFieldsFormLayout_cf_116",
    regstate: "requestData_CustomFieldsFormLayout_cf_121",
    phone:    "requestData_CustomFieldsFormLayout_cf_54",
    reason:   "requestData_CustomFieldsFormLayout_cf_118",
    date:     "requestData_CustomFieldsFormLayout_cf_119"
  };

  var coll = window.ASPxClientControl && ASPxClientControl.GetControlCollection();
  if (!coll || !coll.GetByName(N.email)) {
    if (confirm("This button works on the town's Overnight Parking Request form.\n\nOpen the form now? (Tap the button again once it loads.)")) {
      location.href = FORM_URL;
    }
    return;
  }
  function ctl(name) { return coll.GetByName(name); }

  /* ---------- status banner ---------- */
  var old = document.getElementById("apw-banner");
  if (old) old.remove();
  var bar = document.createElement("div");
  bar.id = "apw-banner";
  bar.style.cssText = "position:fixed;left:8px;top:8px;width:calc(100vw - 16px);box-sizing:border-box;z-index:2147483647;" +
    "background:#1d2b3a;color:#fff;font:15px/1.4 -apple-system,system-ui,sans-serif;" +
    "padding:12px 14px;border-radius:10px;box-shadow:0 6px 24px rgba(0,0,0,.35)";
  document.body.appendChild(bar);
  var lines = [];
  function render(extraHtml) {
    bar.innerHTML = lines.join("<br>") + (extraHtml || "") +
      '<a href="#" id="apw-x" style="position:absolute;top:6px;right:10px;color:#9fb3c8;text-decoration:none;font-size:20px">&times;</a>';
    document.getElementById("apw-x").onclick = function (e) { e.preventDefault(); bar.remove(); };
  }
  function say(msg) { lines.push(msg); render(); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return "&#" + c.charCodeAt(0) + ";"; }); }

  /* ---------- helpers ---------- */
  function setText(name, value) {
    if (value == null || value === "") return;
    ctl(name).SetValue(String(value));
  }

  // Pick a fixed-list combobox item by text: exact match first, then prefix.
  function setCombo(name, value) {
    if (!value) return false;
    var c = ctl(name), want = String(value).trim().toLowerCase(), hit = -1;
    for (var pass = 0; pass < 2 && hit < 0; pass++) {
      for (var i = 0; i < c.GetItemCount(); i++) {
        var t = (c.GetItem(i).text || "").trim().toLowerCase();
        if (t && (pass === 0 ? t === want : t.indexOf(want) === 0)) { hit = i; break; }
      }
    }
    if (hit < 0) return false;
    c.SetSelectedIndex(hit);
    c.RaiseValueChanged();
    return true;
  }

  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function fmt(d) { return pad(d.getMonth() + 1) + "/" + pad(d.getDate()) + "/" + d.getFullYear(); }
  // The town wants the "actual" date of the 1am-7am window: a request for
  // Saturday night uses Sunday's date. So "tonight" is tomorrow's date, unless
  // it's already past midnight (before 7am), when it's today's.
  function setDate(extraNights) {
    var d = new Date();
    var startOffset = d.getHours() < 7 ? 0 : 1;
    d.setHours(0, 0, 0, 0);
    d.setDate(d.getDate() + startOffset + extraNights);
    var c = ctl(N.date);
    c.SetDate(d);
    c.RaiseValueChanged();
    return d;
  }

  // Address lookup: the list is filtered on the server as you type. Put the
  // text in the box, fire the same filter the keyboard would, and wait for
  // the results. Try the full address first; if the town spells it
  // differently ("Street" vs "ST"), retry with just the number and the first
  // word of the street and take it if that leaves only one address.
  function setAddress(done) {
    var c = ctl(N.addr1), inp = c.GetInputElement();
    var want = String(cfg.address || "").toUpperCase().replace(/[.,]/g, " ").replace(/\s+/g, " ").trim();
    var unit = String(cfg.unit || "").trim().toUpperCase();
    if (!want) return done(false, "no address saved");

    function query(text, cb) {
      inp.focus();
      inp.value = text;
      c.filterStrategy.OnInput();
      var tries = 0;
      (function poll() {
        tries++;
        var busy = (c.InCallback && c.InCallback()) ||
          (c.filterStrategy.IsFilterTimerActive && c.filterStrategy.IsFilterTimerActive());
        if ((busy || tries < 4) && tries < 50) return setTimeout(poll, 200); // up to ~10s
        var items = [];
        for (var i = 0; i < c.GetItemCount(); i++) {
          var it = c.GetItem(i);
          if (it.text && it.text.trim()) items.push({ i: i, text: it.text.toUpperCase().trim(), value: it.value || "" });
        }
        cb(items);
      })();
    }

    function choose(cands) {
      var pick = cands[0];
      if (unit) {
        for (var k = 0; k < cands.length; k++) {
          if (cands[k].value.split(",")[0].toUpperCase() === unit) { pick = cands[k]; break; }
        }
      }
      c.SetSelectedIndex(pick.i);
      c.RaiseSelectedIndexChanged();
      c.RaiseValueChanged();
      c.HideDropDown && c.HideDropDown();
      inp.blur();
      done(true, pick.text);
    }

    function giveUp(items, text) {
      // Leave the filtered list open so the person can pick their address.
      c.ShowDropDown && c.ShowDropDown();
      done(false, items.length ? "pick yours from the list" : "the town's list has no match for \u201c" + text + "\u201d");
    }

    query(want, function (items) {
      var exact = items.filter(function (x) { return x.text === want; });
      if (exact.length) return choose(exact);
      var m = want.match(/^(\d+[A-Z]?)\s+(\S+)/);
      if (!m) return giveUp(items, want);
      var short = m[1] + " " + m[2];
      query(short, function (items2) {
        var names = {};
        items2.forEach(function (x) { names[x.text] = true; });
        if (Object.keys(names).length === 1) return choose(items2);
        giveUp(items2, short);
      });
    });
  }

  /* ---------- fill ---------- */
  say("Filling the parking form…");
  var problems = [];
  try {
    setText(N.email, cfg.email);
    setText(N.unit, cfg.unit);
    setText(N.plate, String(cfg.plate || "").toUpperCase().replace(/\s+/g, ""));
    setText(N.phone, cfg.phone);
    if (!setCombo(N.regstate, cfg.plateState || "MA")) problems.push("plate state");
    if (!setCombo(N.reason, cfg.reason || "Guest Visiting")) problems.push("reason");
  } catch (e) {
    problems.push("unexpected error: " + e.message);
  }

  var offset = 0;
  var dateObj;
  try { dateObj = setDate(offset); } catch (e) { problems.push("date"); }

  setAddress(function (ok, info) {
    lines = [];
    if (!ok) problems.unshift("address (" + info + ")");
    if (problems.length) {
      lines.push("<b>Almost done.</b> Please fill in: " + esc(problems.join(", ")) + ".");
    } else {
      lines.push("<b>✓ Form filled.</b> Check it over, then press <b>Submit</b>.");
    }
    drawDate();
  });

  function drawDate() {
    var label = dateObj ? fmt(dateObj) : "?";
    render('<br>Date: <b id="apw-d">' + label + "</b> (" + (offset ? "for tomorrow night" : "for tonight") + ") " +
      '<a href="#" id="apw-t" style="color:#8ec5ff">' + (offset ? "switch to tonight" : "switch to tomorrow night") + "</a>");
    document.getElementById("apw-t").onclick = function (e) {
      e.preventDefault();
      offset = offset ? 0 : 1;
      dateObj = setDate(offset);
      drawDate();
    };
  }
})(__CFG__);
