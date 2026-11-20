JSON.stringify((function () {
  var out = {};

  // 1) 检查注入的 slot 兜底是否在位
  try {
    var gp = null;
    for (var k in SugarCube.macros) { }
    // 从 Story 里找 generateshoppage 的源码
    var found = false;
    if (SugarCube.Story && SugarCube.Story.passages && SugarCube.Story.passages.length) {
      for (var i = 0; i < SugarCube.Story.passages.length; i++) {
        var p = SugarCube.Story.passages[i];
        if (p && p.text && p.text.indexOf("generateshoppage") >= 0 && p.text.indexOf("_realSlot to") >= 0) {
          var mm = p.text.match(/<<set \$_realSlot to \([^>]*\)>>/);
          if (mm) { out.slotExpr = mm[0].slice(0, 400); found = true; }
          break;
        }
      }
    }
    out.slotExprFound = found;
  } catch (e) { out.slotErr = String(e).slice(0, 200); }

  // 2) 统计 setup.clothes 里缺 slot 的服装数
  try {
    var missing = [], total = 0;
    for (var sk in setup.clothes) {
      if (sk === "all" || !Array.isArray(setup.clothes[sk])) continue;
      for (var j = 0; j < setup.clothes[sk].length; j++) {
        var c = setup.clothes[sk][j];
        total++;
        if (c && !c.slot) missing.push(sk + ":" + (c.name || c.variable || "?"));
      }
    }
    out.clothesTotal = total;
    out.missingSlotCount = missing.length;
    out.missingSample = missing.slice(0, 12);
  } catch (e) { out.clothesErr = String(e).slice(0, 200); }

  // 3) 实际跑一次兜底表达式，看能不能找到 slot
  try {
    var targets = ["dragonbreath", "Queen of heart", "acorn", "Sweetsnowsuit"];
    out.resolved = {};
    for (var t = 0; t < targets.length; t++) {
      var nm = targets[t];
      var item = null;
      for (var sk2 in setup.clothes) {
        if (sk2 === "all" || !Array.isArray(setup.clothes[sk2])) continue;
        var hit = setup.clothes[sk2].find(function (x) { return x && x.name === nm; });
        if (hit) { item = hit; break; }
      }
      if (!item) { out.resolved[nm] = "NOT_FOUND"; continue; }
      var slot = item.slot || Object.keys(setup.clothes).find(function (kk) {
        return kk !== "all" && Array.isArray(setup.clothes[kk]) &&
          setup.clothes[kk].some(function (x) { return x && x.index === item.index; });
      }) || "upper";
      out.resolved[nm] = { index: item.index, slot: slot, hasSlotField: !!item.slot };
    }
  } catch (e) { out.resolveErr = String(e).slice(0, 200); }

  return out;
})())
