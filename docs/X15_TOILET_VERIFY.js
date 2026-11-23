// 验证 Toilet Addon 的 4 个场景 + Bathroom 运行时解手入口
(() => {
  const S = window.SugarCube;
  const out = {};
  const check = (name) => {
    try {
      S.Engine.play(name);
      const html = jQuery(".passage").last().html() || "";
      return {
        exists: S.Story.has(name),
        pee: (html.match(/小便/g) || []).length,
        poo: (html.match(/大便/g) || []).length,
        len: html.length,
      };
    } catch (e) { return { exists: S.Story.has(name), err: String(e).slice(0, 60) }; }
  };
  out.innBathroom = check("Inn Bathroom");
  out.innBath = check("Inn Bath");
  out.flatsShower = check("Flats Own Shower");
  out.deadwood = check("Deadwood Reblooms Property Bathroom");
  out.orphanBathroom = check("Bathroom");
  return out;
})()
