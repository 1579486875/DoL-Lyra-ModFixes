JSON.stringify((function () {
  var out = {};
  function testMacro(expr) {
    try {
      var d = document.createElement("div");
      $(d).wiki(expr);
      var t = (d.textContent || "").trim();
      if (/does not exist/.test(t)) return "MISSING";
      if (/出错/.test(t)) return "ERRORS:" + t.slice(0, 80);
      return "OK:" + t.slice(0, 40);
    } catch (e) { return "THROW:" + String(e.message).slice(0, 60); }
  }

  out.tests = {
    flight_text: testMacro("<<flight_text>>"),
    QUANTIFIER: testMacro('<<QUANTIFIER_OF_FOODS_CN "drink">>'),
    UPDATE_CLOTH: testMacro('<<UPDATE_CLOTH_CN "shirt">>'),
    temple_rank: testMacro("<<temple_rank>>"),
    pcpetname: testMacro('<<pcpetname "Gwylan" "good">>'),
    pluralise: testMacro('<<pluralise 3 "sample">>'),
    rngWraith: testMacro("<<rngWraith>>"),
    wHunt: testMacro("<<wHunt>>")
  };

  // printNobody 应该已变成纯文本
  out.printNobodyLeft = (function () {
    var s = document.documentElement.innerHTML || "";
    return s.indexOf("printNobody") >= 0;
  })();

  // 检查「无人」是否出现在侧栏相关位置
  out.hasWuren = (document.body ? (document.body.textContent || "").indexOf("无人") >= 0 : false);

  return out;
})())
