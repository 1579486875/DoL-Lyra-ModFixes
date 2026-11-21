(function () {
  var s = SugarCube.setup, out = {};
  try {
    var t = s.NPCTypeList_cn_name;
    out.tableType = typeof t;
    out.tableLen = t ? String(t).length : 0;
    out.hasHerring = t ? String(t).indexOf("herring,") : -2;
    ["herring", "cod", "trout", "wolf", "bass", "eels", "salmon", "pike", "carp", "perch", "tuna", "mackerel", "whiting"].forEach(function (k) {
      try { out["t_" + k] = s.NPC_CN_TYPE(k); } catch (e) { out["t_" + k] = "ERR " + e.message; }
    });
    var fish = s.fishing && s.fishing.lootTables && s.fishing.lootTables.fish;
    out.fishKeys = fish ? Object.keys(fish) : null;
    out.fishUntranslated = fish ? Object.keys(fish).filter(function (k) { return s.NPC_CN_TYPE(k) === k; }) : null;
    out.fnSrc = String(s.NPC_CN_TYPE).slice(0, 200);
  } catch (e) { out.err = String(e); }
  return JSON.stringify(out);
})()
