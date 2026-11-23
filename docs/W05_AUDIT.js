// 第5轮：运行时接管审计 —— 逐个函数看实际函数体特征 + 全词条抽查
(() => {
  const st = window.setup;
  const out = { fns: {}, sample: {} };

  const FNS = ["NPC_CN_NAME", "NPC_CN_TYPE", "NPC_CN_TITLE", "NPC_CN_TOOLNAME",
               "BODYPARTS_CN_NAME", "description_CN"];
  FNS.forEach(fn => {
    const f = st[fn];
    if (typeof f !== "function") { out.fns[fn] = "NOT_FUNCTION:" + typeof f; return; }
    const src = f.toString();
    out.fns[fn] = {
      len: src.length,
      hasMakeFn: src.indexOf("h.orig") >= 0,
      hasFallback: src.indexOf("fullDescription") >= 0 || src.indexOf("typeTable") >= 0,
      hasTableScan: src.indexOf("NPCTypeList_cn_name") >= 0 || src.indexOf("_keys0") >= 0,
    };
  });

  // 词条抽查（历史修复点全部复查）
  const t = (fn, ks) => { const r = {}; ks.forEach(k => { try { r[k] = st[fn](k); } catch (e) { r[k] = "ERR"; } }); return r; };
  out.sample.title = t("NPC_CN_TITLE", ["baker", "bartender", "chef", "alpha", "mayor", "farmer", "captain", "horror", "smuggler", "faithful", "reflection", "photographer", "farmhand", "terror", "anonymous"]);
  out.sample.type = t("NPC_CN_TYPE", ["wolf", "fish", "shark", "giant slime", "carp", "starfish", "plantgirl", "slim plantgirl", "human"]);
  out.sample.name = t("NPC_CN_NAME", ["Robin", "slim plantgirl", "Robust plantgirl", "lissome man", "curvy catgirl", "thick dog"]);
  out.sample.tool = t("NPC_CN_TOOLNAME", ["pen", "pencil", "marker", "dildo", "brush", "crayon", "quill", "chalk"]);
  out.sample.body = t("BODYPARTS_CN_NAME", ["right", "left", "hand", "right hand", "left hand", "foot", "arm"]);
  out.sample.desc = t("description_CN", ["lissome", "slender", "curvy", "slim", "robust", "thick", "brutish", "burly", "fit", "graceful", "heavyset", "lush", "mousy", "plush", "shapely", "voluptuous", "vulgar", "wide-eyed", "minor demon", "demon"]);
  return out;
})()
