// T02: 单元测试 slot 兜底 —— 先把 SugarCube 语法转成 JS

const fs = require("fs");
const raw = fs.readFileSync("E:/TAML/_dol/work/index_apk.html", "utf8");
function unesc(s) {
  return s.replace(/&lt;/g, "<").replace(/&gt;/g, ">")
          .replace(/&quot;/g, '"').replace(/&#39;/g, "'")
          .replace(/&amp;/g, "&");
}
const g = unesc(raw);

const m = g.match(/<<set \$_realSlot to \(([\s\S]{0,600}?)\)>>/);
if (!m) { console.log("❌ 找不到表达式"); process.exit(1); }
let expr = m[1];
console.log("=== SugarCube 原表达式 ===");
console.log(expr);
console.log();

// SugarCube -> JS 的最小翻译
let js = expr
  .replace(/\$([A-Za-z_][A-Za-z0-9_]*)/g, "_$1")   // $var -> _var
  .replace(/\bisnot\b/g, "!==")
  .replace(/\bis\b/g, "===");
console.log("=== 转成 JS ===");
console.log(js);
console.log();

const mk = (name, index, set, extra) =>
  Object.assign({ name, index, set, variable: name.replace(/ /g, "_") }, extra || {});

const setup = {
  clothes: {
    all: [],
    upper: [
      mk("普通上衣", 1, "upper", { slot: "upper" }),
      mk("dragonbreath", 261, "dragonbreath"),
      mk("Queen of heart", 262, "Queenofheart"),
      mk("Sweet snow suit", 264, "upper"),
      mk("Alice's dream", 266, "Alice'sdream"),
      mk("acorn", 270, "acorn"),
      mk("Suit for Adventurer", 271, "SuitforAdventurer"),
    ],
    lower: [mk("普通下装", 2, "lower", { slot: "lower" })],
    head: [mk("帽子", 3, "head", { slot: "head" })],
  },
};
setup.clothes.all = [
  ...setup.clothes.upper, ...setup.clothes.lower, ...setup.clothes.head,
];

let fn;
try {
  fn = new Function("setup", "_item", "_clothingShopSlot", "return (" + js + ");");
} catch (e) {
  console.log("❌ 语法错误:", e.message);
  process.exit(1);
}
console.log("✅ 语法合法\n=== 测试 ===");

let pass = 0, fail = 0;
function test(label, item, shopSlot, expect) {
  let got;
  try { got = fn(setup, item, shopSlot); }
  catch (e) { console.log(`  ❌ ${label}: 抛异常 ${e.message}`); fail++; return; }
  const ok = got === expect;
  console.log(`  ${ok ? "✅" : "❌"} ${label}: ${JSON.stringify(got)}${ok ? "" : "  (期望 " + expect + ")"}`);
  ok ? pass++ : fail++;
}

test("普通上衣（有 slot）", setup.clothes.upper[0], "all", "upper");
test("普通下装（有 slot）", setup.clothes.lower[0], "all", "lower");
test("帽子（有 slot）", setup.clothes.head[0], "all", "head");
test("dragonbreath（缺 slot）", setup.clothes.upper[1], "all", "upper");
test("Queen of heart（缺 slot）", setup.clothes.upper[2], "all", "upper");
test("Sweet snow suit（缺 slot）", setup.clothes.upper[3], "all", "upper");
test("Alice's dream（缺 slot）", setup.clothes.upper[4], "all", "upper");
test("acorn（缺 slot）", setup.clothes.upper[5], "all", "upper");
test("Suit for Adventurer（缺 slot）", setup.clothes.upper[6], "all", "upper");
test("指定 upper", setup.clothes.upper[1], "upper", "upper");
test("指定 lower", setup.clothes.upper[1], "lower", "lower");
test("查不到（回退 upper）", mk("不存在的", 9999, "ghost"), "all", "upper");

console.log(`\n结果: ${pass} 通过 / ${fail} 失败`);
process.exit(fail === 0 ? 0 : 1);
