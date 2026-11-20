JSON.stringify((function () {
  var out = { logs: [], errors: [] };

  // 挂全局错误捕获
  if (!window.__brTrapInstalled) {
    window.__brTrapInstalled = true;
    window.__brTrap = [];
    var origErr = window.onerror;
    window.onerror = function (msg, src, line, col, err) {
      window.__brTrap.push({ msg: String(msg), stack: err && err.stack ? err.stack.substr(0, 600) : "" });
      if (origErr) try { origErr.apply(this, arguments); } catch (e) { }
      return false;
    };
    // 拦截 Wikifier 报错
    try {
      if (window.SugarCube && SugarCube.Wikifier) {
        var W = SugarCube.Wikifier;
        var origParse = W.parse;
        if (typeof origParse === "function") {
          W.parse = function () {
            try { return origParse.apply(this, arguments); }
            catch (e) {
              window.__brTrap.push({ msg: "Wikifier.parse: " + e.message, stack: (e.stack || "").substr(0, 600) });
              throw e;
            }
          };
        }
      }
    } catch (e) { }
  }

  // 直接解析 Harvest Street 的源文本，看有没有 <<br>>
  try {
    var ps = Story.get("Harvest Street");
    if (ps) {
      var txt = ps.text || "";
      out.hsLen = txt.length;
      out.hasBr = /<<br\s*>>/.test(txt);
      // 找所有 <<...>> 宏
      var macs = {};
      var re = /<<\s*\/?\s*([A-Za-z_][A-Za-z0-9_-]*)/g, m;
      while ((m = re.exec(txt))) { macs[m[1]] = (macs[m[1]] || 0) + 1; }
      out.hsMacros = Object.keys(macs).sort();
    }
  } catch (e) { out.hsErr = e.message; }

  // 检查 br 宏是否注册
  try {
    out.hasBrMacro = !!(window.SugarCube && SugarCube.macros && SugarCube.macros.br);
  } catch (e) { out.brMacroErr = e.message; }

  // 检查所有 widget 名里有没有 br
  out.trap = window.__brTrap || [];

  return out;
})())
