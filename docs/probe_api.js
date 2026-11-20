JSON.stringify((function () {
  var out = {};

  out.globals = {
    SugarCube: typeof SugarCube,
    Story: typeof Story,
    State: typeof State,
    setup: typeof setup,
    Engine: typeof Engine
  };

  // SugarCube 对象上有哪些 key
  try {
    out.SugarCubeKeys = Object.keys(SugarCube).slice(0, 40);
  } catch (e) { out.scErr = String(e); }

  // Story 上的 key
  try {
    out.StoryKeys = (typeof SugarCube.Story !== "undefined" && SugarCube.Story)
      ? Object.keys(SugarCube.Story).slice(0, 40) : "NO_STORY";
  } catch (e) { out.stErr = String(e); }

  // Story 是否可直接访问
  try {
    out.StoryFromGlobal = (typeof Story !== "undefined" && Story) ? Object.keys(Story).slice(0, 40) : "NO";
  } catch (e) { out.sgErr = String(e); }

  // 试各种获取 passage 列表的方式
  var tries = {};
  function t(label, fn) {
    try { var v = fn(); tries[label] = (v === undefined) ? "undefined" : (v === null ? "null" : (typeof v === "object" ? "obj len=" + (v.length !== undefined ? v.length : "n/a") : String(v).slice(0, 40))); }
    catch (e) { tries[label] = "ERR:" + String(e).slice(0, 50); }
  }
  t("SugarCube.Story.passages", function () { return SugarCube.Story.passages; });
  t("SugarCube.Story.lookup", function () { return SugarCube.Story.lookup; });
  t("SugarCube.Story._passages", function () { return SugarCube.Story._passages; });
  t("Story.passages", function () { return Story.passages; });
  t("Story.get('Start')", function () { return SugarCube.Story.get("Start"); });
  out.tries = tries;

  // Story.get 返回什么
  try {
    var ps = SugarCube.Story.get("Start");
    if (ps) {
      out.startPassageKeys = Object.keys(ps).slice(0, 20);
      out.startTextLen = ps.text ? ps.text.length : "NO_TEXT";
      out.startTextHead = ps.text ? ps.text.slice(0, 100) : "";
    }
  } catch (e) { out.getErr = String(e).slice(0, 100); }

  // Story 有没有遍历方法
  try {
    var methods = [];
    for (var k in SugarCube.Story) {
      if (typeof SugarCube.Story[k] === "function") methods.push(k);
    }
    out.storyMethods = methods.slice(0, 30);
  } catch (e) { out.mErr = String(e).slice(0, 100); }

  return out;
})())
