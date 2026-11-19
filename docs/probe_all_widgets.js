JSON.stringify((function () {
  var SC = window.SugarCube;
  if (!SC || !SC.Macro || !SC.Story) return { error: "NO_SC" };
  var Macro = SC.Macro, Story = SC.Story;

  var list = [];
  try {
    list = Story.lookup("tags", "widget");
  } catch (e) {
    return { error: "LOOKUP:" + e.message, api: Object.keys(Story).slice(0, 20) };
  }

  var total = 0, missing = [], perPassage = {};

  for (var i = 0; i < list.length; i++) {
    var p = list[i];
    try {
      var src = p.text || "";
      if (src.indexOf("<<widget") < 0) continue;
      var re = /<<widget\s+"([^"]+)"\s*>>/g, m, cnt = 0, miss = 0;
      while ((m = re.exec(src)) !== null) {
        total++;
        cnt++;
        if (!Macro.has(m[1])) {
          miss++;
          if (missing.length < 100) missing.push(p.name + "::" + m[1]);
        }
      }
      if (miss) perPassage[p.name] = cnt + "/" + miss;
    } catch (e) { }
  }

  return {
    widgetPassages: list.length,
    totalWidgets: total,
    missingCount: missing.length,
    missing: missing,
    perPassage: perPassage
  };
})())
