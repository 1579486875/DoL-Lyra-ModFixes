// 探针：ModLoader 运行时状态（模组是否真的加载、加载日志里的 warning/error、关键 passage 是否存在）
JSON.stringify((function () {
  var out = {};
  try {
    var mu = window.modUtils;
    out.loadedMods = mu && mu.getModListNameNoAlias ? mu.getModListNameNoAlias() : "NO modUtils";
  } catch (e) { out.loadedModsErr = String(e); }
  try {
    var ml = window.modSC2DataManager.getModLoader();
    out.modLoaderKeys = Object.keys(ml).slice(0, 40);
    try { out.cacheArray = ml.getModCacheArray().map(function (m) { return m.name; }); } catch (e) { out.cacheArrayErr = String(e); }
  } catch (e) { out.mlErr = String(e); }
  try {
    var lp = window.modLoaderGui_LoadingProgress || (window.modLoaderGui && window.modLoaderGui.gLoadingProgress);
    var ll = (lp && lp.logList) || [];
    out.logTotal = ll.length;
    var cnt = {};
    ll.forEach(function (e) { cnt[e.type] = (cnt[e.type] || 0) + 1; });
    out.logByType = cnt;
    out.logWarnErr = ll.filter(function (e) { return e.type === "warning" || e.type === "error"; })
      .map(function (e) { return "[" + e.type + "] " + String(e.str).slice(0, 600); });
    out.logAllTail = ll.slice(-30).map(function (e) { return "[" + e.type + "] " + String(e.str).slice(0, 200); });
  } catch (e) { out.logErr = String(e); }
  try {
    var S = SugarCube.Story;
    out.storyHas = {};
    ["Inn Bathroom", "Inn Bath", "Flats Own Shower", "Deadwood Reblooms Property Bathroom", "Robin Hug Cry",
     "Widgets Repair", "Start", "Clothing Shop v2 Widgets"].forEach(function (n) { out.storyHas[n] = S.has(n); });
    var dw = [];
    try { S.lookupWith(function (p) { if (/deadwood/i.test(p.title) && dw.length < 15) dw.push(p.title); return false; }); } catch (e) { out.lookupErr = String(e); }
    out.deadwoodPassages = dw;
    var all = S.lookupWith(function () { return true; });
    out.passageCount = all.length;
  } catch (e) { out.storyErr = String(e); }
  try {
    var errs = Array.from(document.querySelectorAll(".error-view, .macro-error, .error")).map(function (x) { return x.textContent.slice(0, 300); });
    out.domErrors = errs.slice(0, 20);
    out.domErrorCount = errs.length;
  } catch (e) { }
  return out;
})(), null, 1)
