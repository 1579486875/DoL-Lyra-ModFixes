JSON.stringify((function () {
  var out = {};

  // 1. 缓存标志
  out.installed = setup.__cnTablesInstalled;

  // 2. 函数是否真的装上了
  out.fnType = typeof setup.NPC_CN_TYPE;
  out.fnBody = typeof setup.BODYPARTS_CN_NAME;

  // 3. 直接模拟 parseTable 逻辑，看 bullboy 能否解析
  var s = setup.NPCTypeList_cn_name || "";
  var out2 = {};
  s.split("|").forEach(function (pair) {
    var i = pair.indexOf(",");
    if (i < 0) return;
    var k = pair.slice(0, i).trim();
    var v = pair.slice(i + 1).trim();
    if (k && v) out2[k.toLowerCase()] = v;
  });
  out.parsedCount = Object.keys(out2).length;
  out.parsed_bullboy = out2["bullboy"];
  out.parsed_catboy = out2["catboy"];
  out.parsed_curvy = out2["curvy"];

  // 4. 多次调用看是否稳定
  out.call1 = setup.NPC_CN_TYPE("bullboy");
  out.call2 = setup.NPC_CN_TYPE("bullboy");
  out.call3 = setup.NPC_CN_TYPE("catboy");

  // 5. 测大写/空格变体
  out.variants = {};
  ["bullboy", "BULLBOY", "Bullboy", " bullboy", "bullboy "].forEach(function (k) {
    try { out.variants[JSON.stringify(k)] = setup.NPC_CN_TYPE(k); } catch (e) { }
  });

  // 6. 表里 bullboy 附近的原始片段
  var idx = s.indexOf("bullboy");
  out.rawAround = idx >= 0 ? s.substr(Math.max(0, idx - 40), 80) : "NOT FOUND";

  // 7. 是否有多个 script 块装了 NPC_CN_TYPE
  out.fnStr = String(setup.NPC_CN_TYPE).substr(0, 200);

  return out;
})())
