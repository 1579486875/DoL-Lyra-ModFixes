JSON.stringify((function () {
  var out = { tried: {} };

  // 诊断 SugarCube.Macro 的结构
  try {
    var M = SugarCube.Macro;
    out.MacroType = typeof M;
    out.MacroKeys = M ? Object.keys(M).slice(0, 30) : "NULL";
    out.MacroProto = M ? Object.getOwnPropertyNames(Object.getPrototypeOf(M)).slice(0, 30) : "NULL";
  } catch (e) { out.macroErr = String(e).slice(0, 100); }

  // 试多种查宏的方式
  function probe(label, fn) {
    try {
      var v = fn();
      out.tried[label] = (typeof v === "undefined") ? "undefined"
        : (v === null ? "null" : (typeof v === "function" ? "FUNCTION" : String(v).slice(0, 60)));
    } catch (e) { out.tried[label] = "ERR:" + String(e).slice(0, 50); }
  }

  probe("SugarCube.Macro.has", function () { return typeof SugarCube.Macro.has; });
  probe("Macro.has(relation-box)", function () { return SugarCube.Macro.has("relation-box"); });
  probe("Macro.has(combatperson)", function () { return SugarCube.Macro.has("combatperson"); });
  probe("Macro.has(generateshoppage)", function () { return SugarCube.Macro.has("generateshoppage"); });
  probe("Macro.has(if)", function () { return SugarCube.Macro.has("if"); });
  probe("SugarCube.Macro.get", function () { return typeof SugarCube.Macro.get; });

  // 如果 Macro.get 存在，打印源码
  try {
    if (typeof SugarCube.Macro.get === "function") {
      var names = ["relation-box", "combatperson", "generateshoppage", "straponGeneratorOptions"];
      out.srcs = {};
      for (var i = 0; i < names.length; i++) {
        var n = names[i];
        try {
          var f = SugarCube.Macro.get(n);
          if (!f) { out.srcs[n] = "NULL"; continue; }
          var s = String(typeof f === "object" && f.handler ? f.handler : f);
          out.srcs[n] = {
            len: s.length,
            head: s.slice(0, 150),
            marks: {
              badMacroInIf: s.indexOf("<<if (<<NPC_CN_NAME") >= 0,
              cnDesc: s.indexOf("$description_CN || $description") >= 0,
              slotFallback: s.indexOf("Object.keys(setup.clothes).find") >= 0,
              rawSlot: s.indexOf("? _item.slot :") >= 0,
              regular: s.indexOf('"regular"') >= 0,
              putong: s.indexOf('"普通"') >= 0
            }
          };
        } catch (e2) { out.srcs[n] = "ERR:" + String(e2).slice(0, 60); }
      }
    }
  } catch (e) { out.srcErr = String(e).slice(0, 100); }

  // 兜底：直接搜 DOM 里已渲染的 macro 表（SugarCube 有时挂在 window 上）
  probe("window.macros", function () { return typeof window.macros; });
  probe("window.SugarCube.Macro.size", function () { return SugarCube.Macro.size; });

  return out;
})())
