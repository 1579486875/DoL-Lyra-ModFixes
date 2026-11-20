JSON.stringify((function () {
  var out = {};

  // 1. 表本身
  var s = setup.NPCTypeList_cn_name || "";
  out.tableLen = s.length;
  out.tableItems = s.split("|").length;

  // 2. 找几个关键 key 在表里的位置
  ["bullboy", "lizardgirl", "spidergirl", "harpy", "none", "creature", "catboy"].forEach(function (k) {
    var idx = s.indexOf(k + ",");
    out["pos_" + k] = idx;
    if (idx >= 0) {
      out["val_" + k] = s.substr(idx, 30);
    }
  });

  // 3. 直接调 NPC_CN_TYPE
  ["bullboy", "lizardgirl", "harpy", "none", "creature", "catboy", "curvy"].forEach(function (k) {
    try { out["fn_" + k] = setup.NPC_CN_TYPE(k); } catch (e) { out["fn_" + k] = "ERR:" + e.message; }
  });

  // 4. parseTable 的行为（如果可访问）
  try {
    out.hasParseTable = (typeof parseTable);
  } catch (e) { out.hasParseTable = "INACCESSIBLE"; }

  // 5. 检查 window.PART
  try {
    out.windowPART = (typeof window.PART);
    if (window.PART) {
      out.PART_penis = window.PART["penis"];
      out.PART_size = Object.keys(window.PART).length;
    }
  } catch (e) { out.windowPART = "ERR"; }

  // 6. 直接调 BODYPARTS_CN_NAME
  ["penis", "vagina", "anus"].forEach(function (k) {
    try { out["bp_" + k] = setup.BODYPARTS_CN_NAME(k); } catch (e) { out["bp_" + k] = "ERR:" + e.message; }
  });

  // 7. Macro 对象结构
  try {
    out.macroType = typeof Macro;
    out.macroKeys = Macro ? Object.keys(Macro).slice(0, 12) : null;
    out.hasHas = Macro && (typeof Macro.has);
    // 尝试 get
    if (Macro && typeof Macro.get === "function") {
      out.macroGet_stress = !!Macro.get("stress");
    }
  } catch (e) { out.macroErr = e.message; }

  return out;
})())
