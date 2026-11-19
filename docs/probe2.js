JSON.stringify({
  typeTITLES: typeof TITLES,
  isGlobal: typeof window.TITLES !== "undefined",
  keysCount: (typeof TITLES !== "undefined" && TITLES) ? Object.keys(TITLES).length : -1,
  sample: (typeof TITLES !== "undefined" && TITLES) ? Object.keys(TITLES).slice(0, 30) : null,
  hasLizard: (typeof TITLES !== "undefined" && TITLES) ? ("lizard" in TITLES) : null,
  hasWhale: (typeof TITLES !== "undefined" && TITLES) ? ("whale" in TITLES) : null,
  hasHuman: (typeof TITLES !== "undefined" && TITLES) ? ("human" in TITLES) : null,
  trSrc: typeof tr !== "undefined" ? String(tr).slice(0, 300) : null,
  fnFull: String(setup.NPC_CN_TYPE),
  // 看看还有哪些类似的表
  otherTables: Object.keys(window).filter(function (k) {
    try {
      var v = window[k];
      return v && typeof v === "object" && !Array.isArray(v)
        && Object.keys(v).length > 20
        && Object.keys(v).every(function (x) { return /^[a-z_ ]+$/.test(x); });
    } catch (e) { return false; }
  }).slice(0, 20)
})
