JSON.stringify({
  desc: (function () {
    var d = Object.getOwnPropertyDescriptor(setup, "NPC_CN_TYPE");
    if (!d) return "NO_DESCRIPTOR";
    return {
      hasGet: typeof d.get,
      hasSet: typeof d.set,
      writable: d.writable,
      configurable: d.configurable,
      enumerable: d.enumerable,
      valueType: typeof d.value,
      getSrc: d.get ? String(d.get).slice(0, 200) : null
    };
  })(),
  isOwn: Object.prototype.hasOwnProperty.call(setup, "NPC_CN_TYPE"),
  protoHas: (function(){ try { return typeof Object.getPrototypeOf(setup).NPC_CN_TYPE; } catch(e){ return "ERR"; } })(),
  wrapCount: setup.__cnWrapCount,
  // 试着手动覆盖
  manualTest: (function () {
    try {
      var before = setup.NPC_CN_TYPE("lizard");
      setup.NPC_CN_TYPE = function (x) { return "MANUAL:" + x; };
      var after = setup.NPC_CN_TYPE("lizard");
      return { before: before, after: after, changed: before !== after };
    } catch (e) { return "ERR:" + e.message; }
  })(),
  // defineProperty 试试
  defineTest: (function () {
    try {
      Object.defineProperty(setup, "NPC_CN_TYPE", {
        value: function (x) { return "DEFINE:" + x; },
        writable: true, configurable: true, enumerable: true
      });
      return setup.NPC_CN_TYPE("lizard");
    } catch (e) { return "ERR:" + e.message; }
  })()
})
