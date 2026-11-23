// 诊断：BODYPARTS_CN_NAME 运行时实际是哪个版本
(() => {
  const S = window.SugarCube;
  const out = {};
  const fn = window.setup && setup.BODYPARTS_CN_NAME;
  out.type = typeof fn;
  if (typeof fn === "function") {
    const src = fn.toString();
    out.len = src.length;
    out.head = src.slice(0, 160);
    out.hasRight = src.indexOf('"right"') >= 0 || src.indexOf("'right'") >= 0;
    out.hasPB = src.indexOf("__PB") >= 0;
    out.isMk = src.indexOf("hasOwnProperty.call(table") >= 0;
  }
  out.guards = {
    cnTables: window.setup && setup.__cnTablesInstalled,
    i18n: window.setup && setup.__i18nHelpersInstalled,
    descCN: window.setup && setup.__descCNInstalled,
  };
  out.test = {};
  ["right", "left", "hand", "right hand", "foot"].forEach(k => {
    out.test[k] = window.setup.BODYPARTS_CN_NAME(k);
  });
  return out;
})()
