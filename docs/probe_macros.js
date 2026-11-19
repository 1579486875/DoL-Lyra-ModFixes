JSON.stringify({
  // 1) 用户截图里报 "does not exist" 的宏
  macros: (function () {
    var names = ["rngWraith", "wPersist", "wHunt", "wTimerProgress", "rngWraithSocial",
      "speechWraith", "npc", "streetEffects", "eventstreet", "draindescription",
      "social", "relation-box", "wardrobeContents", "wardrobeList", "man",
      "man-combat", "hand_section", "hand_section_two", "bodywriting_npc_bodypart",
      "beasttype", "genitals", "skintonetext", "paincaption"];
    var o = {};
    names.forEach(function (n) {
      try {
        o[n] = (typeof Macro !== "undefined" && Macro.get) ? (Macro.get(n) ? "OK" : "MISSING") : "NO_API";
      } catch (e) { o[n] = "ERR"; }
    });
    return o;
  })(),
  // 2) 关键函数
  fns: (function () {
    var w = ["description_CN", "NPC_CN_TOOLNAME", "NPC_CN_TYPE", "NPC_CN_NAME",
      "CAFE_FOOD_CN", "DirectionCN", "brothelshowType_CN", "update_cloth_cn"];
    var o = {};
    w.forEach(function (k) { o[k] = typeof setup[k]; });
    return o;
  })(),
  // 3) 试着渲染几个易出错的宏
  render: (function () {
    var tests = {
      rngWraith: "<<rngWraith>>",
      wPersist: "<<wPersist>>",
      wHunt: "<<wHunt>>",
      beasttype: "<<beasttype>>",
      genitals: "<<genitals>>",
      skintonetext: "<<skintonetext>>",
      paincaption: "<<paincaption>>"
    };
    var o = {};
    Object.keys(tests).forEach(function (k) {
      try {
        var d = document.createElement("div");
        $(d).wiki(tests[k]);
        o[k] = "OK:" + (d.textContent || "").slice(0, 40);
      } catch (e) {
        o[k] = "ERR:" + (e.message || String(e)).slice(0, 120);
      }
    });
    return o;
  })(),
  // 4) 检查 relation-box widget 能否渲染（用户报过 Unexpected token '<<'）
  relationBox: (function () {
    try {
      var d = document.createElement("div");
      $(d).wiki("<<relation-box>>");
      return "OK:" + (d.textContent || "").slice(0, 60);
    } catch (e) { return "ERR:" + (e.message || String(e)).slice(0, 150); }
  })()
})
