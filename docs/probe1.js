JSON.stringify({
  tableType: typeof setup.NPCTypeList_cn_name,
  tableLen: (setup.NPCTypeList_cn_name || "").length,
  tableHead: (setup.NPCTypeList_cn_name || "").slice(0, 120),
  hasLizard: (setup.NPCTypeList_cn_name || "").indexOf("lizard,") >= 0,
  fnLen: String(setup.NPC_CN_TYPE).length,
  fnSrc: String(setup.NPC_CN_TYPE).slice(0, 300),
  callLizard: setup.NPC_CN_TYPE("lizard"),
  callWhale: setup.NPC_CN_TYPE("whale"),
  callHuman: setup.NPC_CN_TYPE("human"),
  callEels: setup.NPC_CN_TYPE("eels"),
  hasParseTable: typeof setup.__parseTable,
  allSetupKeys: Object.keys(setup).filter(function (k) {
    return /CN|cn|list|List|Table|table/.test(k);
  }).slice(0, 40)
})
