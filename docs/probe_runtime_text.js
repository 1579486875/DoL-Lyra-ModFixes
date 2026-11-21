// 探针：运行时真实数据（setup.feats / setup.clothes 描述 / 家具描述）是否已被 ModI18N 翻译
JSON.stringify((function () {
  var out = {};
  var cjk = /[\u4e00-\u9fff]/;
  try {
    var f = SugarCube.setup.feats || {};
    var ks = Object.keys(f);
    var t = 0, tc = 0, d = 0, dc = 0, h = 0, hc = 0, sample = [];
    ks.forEach(function (k) {
      var o = f[k] || {};
      if (o.title) { t++; if (cjk.test(o.title)) tc++; }
      if (o.desc) { d++; if (cjk.test(o.desc)) dc++; }
      if (o.hint) { h++; if (cjk.test(o.hint)) hc++; }
      if (sample.length < 6) sample.push([k, o.title, o.desc, o.hint]);
    });
    out.feats = { n: ks.length, title: [t, tc], desc: [d, dc], hint: [h, hc], sample: sample };
  } catch (e) { out.featsErr = String(e); }
  try {
    var c = SugarCube.setup.clothes || {};
    var n = 0, nc = 0, samp = [], en = [];
    Object.keys(c).forEach(function (slot) {
      if (slot === "all" || !Array.isArray(c[slot])) return;
      c[slot].forEach(function (it) {
        if (!it || typeof it.description !== "string" || !it.description) return;
        n++;
        if (cjk.test(it.description)) nc++; else if (en.length < 8) en.push([slot, it.name, it.description]);
        if (samp.length < 4) samp.push([slot, it.name, it.cn_name_cap, it.description]);
      });
    });
    out.clothes = { withDesc: n, cjk: nc, sample: samp, enSample: en };
  } catch (e) { out.clothesErr = String(e); }
  try {
    var fu = SugarCube.setup.furniture || SugarCube.setup.furnitureList || null;
    out.furnitureType = fu ? (Array.isArray(fu) ? "array" : typeof fu) : "none";
  } catch (e) { out.furnErr = String(e); }
  try {
    var fs = SugarCube.setup.foodstuff || {};
    var fk = Object.keys(fs), pc = 0, pn = 0, ps = [];
    fk.forEach(function (k) { var o = fs[k]; if (o && typeof o.plural === "string") { pn++; if (cjk.test(o.plural)) pc++; else if (ps.length < 5) ps.push([k, o.plural, o.name]); } });
    out.foodstuff = { n: fk.length, plural: [pn, pc], enSample: ps, blackberry: fs.blackberry ? [fs.blackberry.name, fs.blackberry.plural] : null };
  } catch (e) { out.foodErr = String(e); }
  try {
    var bh = SugarCube.setup.fishingMinigame && SugarCube.setup.fishingMinigame.behaviors;
    out.fishingBehaviors = bh ? Object.keys(bh).map(function (k) { return [k, bh[k].initialAction, bh[k].initialActionCN]; }) : null;
  } catch (e) { out.fishErr = String(e); }
  return out;
})(), null, 1)
