JSON.stringify({
  repair: (typeof setup !== "undefined" && setup.__widgetRepair) ? setup.__widgetRepair : "NOT_RUN",
  scOk: !!(window.SugarCube && window.SugarCube.Macro && window.SugarCube.Story),
  hasMacro: (function () {
    try { return window.SugarCube.Macro.has("effectsWraith"); } catch (e) { return "ERR:" + e.message; }
  })(),
  passage: (typeof State !== "undefined") ? State.passage : null
})
