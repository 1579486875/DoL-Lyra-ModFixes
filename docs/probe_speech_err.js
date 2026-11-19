JSON.stringify((function () {
  var out = {};

  // 1) 完整渲染 speechWraith，捕获错误正文
  try {
    var d = document.createElement("div");
    $(d).wiki("<<speechWraith>>");
    out.speechWraith_html = (d.innerHTML || "").slice(0, 800);
    out.speechWraith_text = (d.textContent || "").slice(0, 500);
  } catch (e) {
    out.speechWraith_throw = String(e.message || e).slice(0, 300);
  }

  // 2) 单独测那两句 set
  var tests = {
    a: '<<set _t1 to "你_speak。\\\\" + "X" + "\\\\">><<= _t1>>',
    b: '<<set _t2 to "_speaks。\\\\" + "Y" + "\\\\">><<= _t2>>'
  };
  out.directTest = {};
  Object.keys(tests).forEach(function (k) {
    try {
      var d = document.createElement("div");
      $(d).wiki(tests[k]);
      out.directTest[k] = (d.textContent || "").slice(0, 200) || "(空)";
    } catch (e) {
      out.directTest[k] = "THROW:" + String(e.message || e).slice(0, 200);
    }
  });

  // 3) 检查 _line1/_line2 是否在 speechWraith 作用域内定义
  try {
    var d2 = document.createElement("div");
    $(d2).wiki("<<set _line1 to 'AAA'>><<set _line2 to 'BBB'>><<= _line1 + _line2>>");
    out.lineTest = (d2.textContent || "").slice(0, 100);
  } catch (e) {
    out.lineTest = "THROW:" + String(e.message || e).slice(0, 150);
  }

  // 4) effectsWraith 为什么 MISSING —— 检查 speechWraith 之后紧邻的源码
  out.note = "see speechWraith_html for exact error";

  return out;
})())
