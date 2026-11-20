JSON.stringify((function () {
  var out = {};
  var f = setup.BODYPARTS_CN_NAME;
  out.type = typeof f;
  var src = String(f);
  out.srcLen = src.length;
  out.srcHead = src.substr(0, 260);

  // 是否是 mk() 版（含 "table" 参数）
  out.isMk = src.indexOf("table") >= 0 && src.indexOf("__PB") < 0;
  out.isPB = src.indexOf("__PB") >= 0;

  // 直接测
  out.penis = setup.BODYPARTS_CN_NAME("penis");
  out.hand = setup.BODYPARTS_CN_NAME("hand");
  out.buttocks = setup.BODYPARTS_CN_NAME("buttocks");

  // 检查 __cnTablesInstalled 时序
  out.installed = setup.__cnTablesInstalled;

  // 有没有 defineProperty 拦截
  var d = Object.getOwnPropertyDescriptor(setup, "BODYPARTS_CN_NAME");
  out.desc = d ? {
    hasGet: !!d.get, hasSet: !!d.set,
    writable: d.writable, enumerable: d.enumerable,
    configurable: d.configurable,
    valueType: typeof d.value
  } : null;

  // 能不能覆盖（测试后恢复）
  var orig = setup.BODYPARTS_CN_NAME;
  try {
    setup.BODYPARTS_CN_NAME = function (x) { return "TEST_" + x; };
    out.canOverwrite = (setup.BODYPARTS_CN_NAME("penis") === "TEST_penis");
    setup.BODYPARTS_CN_NAME = orig;
    out.restored = (setup.BODYPARTS_CN_NAME("penis") === "penis" || setup.BODYPARTS_CN_NAME("penis") !== "TEST_penis");
  } catch (e) {
    out.overwriteErr = e.message;
  }

  // 再测一遍，看是否被谁重置
  out.afterTest_penis = setup.BODYPARTS_CN_NAME("penis");
  out.afterTest_hand = setup.BODYPARTS_CN_NAME("hand");

  return out;
})())
