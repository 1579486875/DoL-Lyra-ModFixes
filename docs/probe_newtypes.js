JSON.stringify((function () {
  var out = {};
  var names = ["doggirl", "dogboy", "catgirl", "catboy", "wolfgirl", "wolfboy",
    "beargirl", "harpygirl", "slimegirl", "plantgirl", "foxgirl", "horsegirl"];
  out.types = {};
  names.forEach(function (n) {
    try { out.types[n] = setup.NPC_CN_TYPE(n); } catch (e) { out.types[n] = "ERR"; }
  });

  // 身形 textMap
  try {
    var o = setup.options && setup.options.bodyType;
    out.bodyType = o ? o.textMap : "NO_OPT";
  } catch (e) { out.bodyType = "ERR"; }

  // 找 curvy 显示
  try {
    out.curvyCheck = (function () {
      var found = null;
      try {
        Object.keys(setup).forEach(function (k) {
          var v = setup[k];
          if (v && typeof v === "object" && v.textMap && v.textMap.curvy) {
            found = v.textMap;
          }
        });
      } catch (e) { }
      return found;
    })();
  } catch (e) { }

  out.passage = (typeof State !== "undefined") ? State.passage : null;
  return out;
})())
