JSON.stringify((function () {
  var out = { passagesWithTargets: {} };
  var P = SugarCube.Story.passages;
  out.total = P.length;

  // 先把三个目标 widget 所在 passage 找出来（用宽松匹配）
  var targets = {
    "relation-box": /widget\s+["']relation-box["']/,
    "generateshoppage": /widget\s+["']generateshoppage["']/,
    "combatperson": /widget\s+["']combatperson["']/
  };

  var found = {};
  for (var t in targets) found[t] = [];

  for (var i = 0; i < P.length; i++) {
    var p = P[i];
    if (!p || !p.text) continue;
    for (var t2 in targets) {
      if (targets[t2].test(p.text)) {
        found[t2].push({ name: p.name, len: p.text.length });
      }
    }
  }
  out.passagesWithTargets = found;

  // 详细检查每个
  function checkWidget(widgetName, marker, markerDesc) {
    var res = { widget: widgetName, passages: found[widgetName] || [], checks: [] };
    for (var i = 0; i < P.length; i++) {
      var p = P[i];
      if (!p || !p.text) continue;
      if (!targets[widgetName].test(p.text)) continue;
      res.checks.push({
        passage: p.name,
        hasMarker: p.text.indexOf(marker) >= 0,
        markerDesc: markerDesc,
        snippet: p.text.substring(Math.max(0, p.text.indexOf(widgetName) - 40), p.text.indexOf(widgetName) + 200)
      });
    }
    return res;
  }

  out.relationBox = checkWidget("relation-box", "$wraith.mimic is _npcData.nam", "比较用英文原名");
  out.slotFix = checkWidget("generateshoppage", "Object.keys(setup.clothes).find", "slot 兜底");
  out.combatCN = checkWidget("combatperson", "$description_CN || $description", "CN 优先");

  // 额外：直接搜关键字，不限定 widget
  out.globalCounts = {
    "Object.keys(setup.clothes).find": 0,
    "$description_CN || $description": 0,
    "$wraith.mimic is _npcData.nam": 0,
    "_realSlot to": 0
  };
  for (var j = 0; j < P.length; j++) {
    var q = P[j];
    if (!q || !q.text) continue;
    for (var k in out.globalCounts) {
      if (q.text.indexOf(k) >= 0) out.globalCounts[k]++;
    }
  }

  return out;
})())
