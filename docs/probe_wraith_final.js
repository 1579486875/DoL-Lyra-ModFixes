JSON.stringify((function () {
  var SC = window.SugarCube;
  var out = {};

  // 1) 直接查 Macro.has（最可靠）
  var names = ["rngWraith", "wHunt", "wPersist", "wraithIntro", "wraithCaught",
    "wraith_pass", "wraithPossess", "wraithExorcise", "gobsession", "lobsession",
    "possessedWord", "effectsWraith", "speechWraith", "kissWraith", "ejacW",
    "exitWraith", "rngWraithSocial", "wraithEventStreet", "wraithEventSewers"];
  out.has = {};
  names.forEach(function (n) { out.has[n] = SC.Macro.has(n); });

  // 2) 实际调用（看是否抛错）
  out.call = {};
  names.forEach(function (n) {
    try {
      var d = document.createElement("div");
      $(d).wiki("<<" + n + ">>");
      var t = (d.textContent || "");
      if (/does not exist/.test(t)) out.call[n] = "MISSING";
      else if (/出错|error within/.test(t)) out.call[n] = "ERRORS";
      else out.call[n] = "OK";
    } catch (e) { out.call[n] = "THROW"; }
  });

  // 3) 统计
  var ok = 0, miss = 0, err = 0;
  for (var k in out.call) {
    if (out.call[k] === "OK") ok++;
    else if (out.call[k] === "MISSING") miss++;
    else err++;
  }
  out.summary = { ok: ok, missing: miss, errors: err, total: names.length };

  // 4) Widgets Repair 是否参与
  var p = SC.Story.get("Widgets Repair");
  out.repairPassage = p ? { len: p.text.length, exists: true } : { exists: false };

  return out;
})())
