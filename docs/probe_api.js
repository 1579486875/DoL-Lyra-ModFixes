JSON.stringify((function () {
  var out = {};
  out.types = {
    Macro: typeof Macro,
    Story: typeof Story,
    Wikifier: typeof Wikifier,
    Engine: typeof Engine,
    State: typeof State,
    Scripting: typeof Scripting,
    SugarCube: typeof SugarCube
  };
  out.sc = window.SugarCube ? Object.keys(window.SugarCube).slice(0, 40) : null;

  // Macro 的能力
  try { out.macroAdd = typeof Macro.add; } catch (e) { out.macroAdd = "ERR"; }
  try { out.macroHas = typeof Macro.has; } catch (e) { out.macroHas = "ERR"; }
  try { out.macroGet = typeof Macro.get; } catch (e) { out.macroGet = "ERR"; }
  try { out.macroDelete = typeof Macro.delete; } catch (e) { out.macroDelete = "ERR"; }

  // Story 的能力
  try { out.storyGet = typeof Story.get; } catch (e) { out.storyGet = "ERR"; }
  try {
    var p = Story.get("Widgets Wraith");
    out.passageOk = !!p;
    out.passageTextLen = p ? p.text.length : 0;
    out.processTextType = p ? typeof p.processText : "N/A";
    if (p && typeof p.processText === "function") {
      out.processedLen = p.processText().length;
    }
  } catch (e) { out.storyErr = String(e.message).slice(0, 150); }

  // 检查 effectsWraith 是否真的不在
  try {
    var d1 = document.createElement("div");
    $(d1).wiki('<<effectsWraith>>');
    out.effectsWraithRender = (d1.textContent || "").slice(0, 150);
  } catch (e) { out.effectsWraithRender = "THROW:" + String(e.message).slice(0, 100); }

  // 试着从一个已知存在的 widget 复制
  try {
    var d2 = document.createElement("div");
    $(d2).wiki('<<checkWraith>>');
    out.checkWraithRender = (d2.textContent || "").slice(0, 100) || "(空但无错)";
  } catch (e) { out.checkWraithRender = "THROW:" + String(e.message).slice(0, 100); }

  return out;
})())
