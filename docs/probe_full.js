JSON.stringify((function () {
  var out = { errors: [], stats: {} };

  // 1. NPC_CN_TYPE 抽 40 个
  var types = ["human", "cat", "catboy", "catgirl", "dog", "doggirl", "dogboy",
    "wolf", "wolfgirl", "bear", "beargirl", "pig", "piggirl", "fox", "foxgirl",
    "horse", "horsegirl", "cow", "bull", "bullboy", "lizard", "lizardgirl",
    "spider", "spidergirl", "harpy", "harpygirl", "slime", "slimegirl",
    "plant", "plantgirl", "dolphin", "dolphingirl", "whale", "eel", "eels",
    "squid", "octopus", "tentacle", "none", "creature"];
  var tOK = 0, tFail = [];
  types.forEach(function (t) {
    try {
      var r = setup.NPC_CN_TYPE(t);
      if (r && r !== t && /[\u4e00-\u9fff]/.test(r)) { tOK++; }
      else { tFail.push(t + " -> " + r); }
    } catch (e) { tFail.push(t + " ERR"); }
  });
  out.stats.NPC_CN_TYPE = tOK + "/" + types.length;
  if (tFail.length) out.errors.push({ fn: "NPC_CN_TYPE", fail: tFail.slice(0, 10) });

  // 2. NPC_CN_NAME 抽 20 个
  var names = ["Robin", "Whitney", "Kylar", "Eden", "Avery", "Alex", "Sydney",
    "Bailey", "Leighton", "Quinn", "Gwylan", "Black Wolf", "Great Hawk",
    "Ivory Wraith", "Mason", "Doren", "Jordan", "River", "Wren", "Charlie"];
  var nOK = 0, nFail = [];
  names.forEach(function (n) {
    try {
      var r = setup.NPC_CN_NAME(n);
      if (r && /[\u4e00-\u9fff]/.test(r)) { nOK++; }
      else { nFail.push(n + " -> " + r); }
    } catch (e) { nFail.push(n + " ERR"); }
  });
  out.stats.NPC_CN_NAME = nOK + "/" + names.length;
  if (nFail.length) out.errors.push({ fn: "NPC_CN_NAME", fail: nFail.slice(0, 10) });

  // 3. BODYPARTS_CN_NAME 抽 15 个
  var parts = ["penis", "vagina", "anus", "breasts", "mouth", "tongue", "hand",
    "foot", "thigh", "buttocks", "tail", "wings", "horn", "ear", "face"];
  var pOK = 0, pFail = [];
  parts.forEach(function (p) {
    try {
      var r = setup.BODYPARTS_CN_NAME(p);
      if (r && /[\u4e00-\u9fff]/.test(r)) { pOK++; }
      else { pFail.push(p + " -> " + r); }
    } catch (e) { pFail.push(p + " ERR"); }
  });
  out.stats.BODYPARTS_CN_NAME = pOK + "/" + parts.length;
  if (pFail.length) out.errors.push({ fn: "BODYPARTS_CN_NAME", fail: pFail.slice(0, 10) });

  // 4. description_CN 抽 10 个
  var descs = ["tall", "short", "slim", "curvy", "athletic", "slender",
    "average", "petite", "muscular", "thin"];
  var dOK = 0, dFail = [];
  descs.forEach(function (d) {
    try {
      var r = setup.description_CN(d);
      if (r && /[\u4e00-\u9fff]/.test(r)) { dOK++; }
      else { dFail.push(d + " -> " + r); }
    } catch (e) { dFail.push(d + " ERR"); }
  });
  out.stats.description_CN = dOK + "/" + descs.length;
  if (dFail.length) out.errors.push({ fn: "description_CN", fail: dFail.slice(0, 10) });

  // 5. NPCTypeList_cn_name 表大小
  try {
    var s = setup.NPCTypeList_cn_name || "";
    out.stats.NPCTypeList_items = s.split("|").length;
    out.stats.NPCTypeList_len = s.length;
  } catch (e) { }

  // 6. 关键宏是否注册
  var macros = ["stress", "pain", "arousal", "trauma", "money", "worn",
    "beasttype", "person1", "personselect", "danceaudience", "actionsman"];
  var mOK = 0, mFail = [];
  macros.forEach(function (m) {
    try {
      if (Macro.has(m)) { mOK++; } else { mFail.push(m); }
    } catch (e) { mFail.push(m + " ERR"); }
  });
  out.stats.macros = mOK + "/" + macros.length;
  if (mFail.length) out.errors.push({ fn: "Macro.has", fail: mFail });

  return out;
})())
