// T06：Npc Name CN 1.4.0 查名顺序单测（不需要浏览器）
const fs = require("fs");
const path = require("path");
const src = fs.readFileSync(process.argv[2], "utf8");
const html = fs.readFileSync(process.argv[3], "utf8").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
const setup = {};
for (const k of ["NPCTypeList_cn_name", "NPCNameList_cn_name", "NPCTitleList_cn_name"]) {
  const m = new RegExp(`<<set setup\\.${k} to "([^"]*)">>`).exec(html);
  setup[k] = m ? m[1] : undefined;
}
global.window = { SugarCube: { setup, macros: { has: () => true, add() {} } } };
global.$ = () => ({ on() {} });
global.setInterval = (f) => { f(); return 1; };
global.clearInterval = () => {};
eval(src);
const ST = window.SugarCube.setup;
let pass = 0, fail = 0;
const eq = (n, a, b) => { if (a === b) { pass++; console.log("  ✅ " + n + " = " + a); } else { fail++; console.log("  ❌ " + n + " = " + a + "（应为 " + b + "）"); } };
eq("type herring", ST.NPC_CN_TYPE("herring"), "鲱鱼");
eq("type cod", ST.NPC_CN_TYPE("cod"), "鳕鱼");
eq("type wolf", ST.NPC_CN_TYPE("wolf"), "狼");
eq("type fish（官方错译覆盖）", ST.NPC_CN_TYPE("fish"), "鱼");
eq("type baitfish（官方缺）", ST.NPC_CN_TYPE("baitfish"), "饵鱼");
eq("type 不存在原样", ST.NPC_CN_TYPE("zzqq"), "zzqq");
eq("type undefined", ST.NPC_CN_TYPE(undefined), "");
eq("name Jordan（官方）", ST.NPC_CN_NAME("Jordan"), "约旦");
eq("name Robin", ST.NPC_CN_NAME("Robin"), "罗宾");
eq("name Seath（内置/合并）", ST.NPC_CN_NAME("Seath"), "希斯");
eq("title businessperson（官方）", ST.NPC_CN_TITLE("businessperson"), "商人");
eq("title guardian", ST.NPC_CN_TITLE("guardian"), "监护人");
eq("part leftArm", ST.BODYPARTS_CN_NAME("leftArm"), "左臂");
// 缓存：表被改写后重新解析
setup.NPCTypeList_cn_name = "herring,鲱鱼X";
eq("表改写后重新解析", ST.NPC_CN_TYPE("herring"), "鲱鱼X");
console.log(`\n结果: ${pass} 通过 / ${fail} 失败`);
process.exit(fail ? 1 : 0);
