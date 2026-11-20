// T01: 单元测试 generateshoppage 的 slot 兜底表达式
// 用模拟的 setup.clothes 验证：缺 slot 的 mod 服装能不能被正确解析出真实栏位

const fs = require("fs");

// 1) 从 index 里把真实表达式抠出来
const raw = fs.readFileSync(
  "E:/TAML/_dol/work/index_apk.html", "utf8"
);
function unesc(s) {
  return s.replace(/&lt;/g, "<").replace(/&gt;/g, ">")
          .replace(/&quot;/g, '"').replace(/&#39;/g, "'")
          .replace(/&amp;/g, "&");
}
const g = unesc(raw);

const m = g.match(/<<set \$_realSlot to \(([\s\S]{0,600}?)\)>>/);
if (!m) {
  console.log("❌ 找不到 _realSlot 表达式");
  process.exit(1);
}
const expr = m[1];
console.log("=== 抽出的表达式 ===");
console.log(expr);
console.log();

// 2) 构造模拟数据：复现报错里的真实物品
const mk = (name, index, set, extra) => Object.assign({
  name, index, set, variable: name.replace(/ /g, "_"),
}, extra || {});

const setup = {
  clothes: {
    all: [],
    upper: [
      mk("普通上衣", 1, "upper", { slot: "upper" }),
      // ↓ 报错里的那些 —— 有 set 但没有 slot
      mk("dragonbreath", 261, "dragonbreath"),
      mk("Queen of heart", 262, "Queenofheart"),
      mk("Sweet snow suit", 264, "upper"),
      mk("Alice's dream", 266, "Alice'sdream"),
      mk("acorn", 270, "acorn"),
      mk("Suit for Adventurer", 271, "SuitforAdventurer"),
    ],
    lower: [
      mk("普通下装", 2, "lower", { slot: "lower" }),
    ],
    head: [
      mk("帽子", 3, "head", { slot: "head" }),
    ],
  },
};
setup.clothes.all = [
  ...setup.clothes.upper, ...setup.clothes.lower, ...setup.clothes.head,
];

// 3) 编译并执行表达式
let fn;
try {
  fn = new Function("setup", "_item", "_clothingShopSlot", "return (" + expr + ");");
} catch (e) {
  console.log("❌ 表达式语法错误:", e.message);
  process.exit(1);
}
console.log("✅ 表达式语法合法\n");

console.log("=== 测试 ===");
let pass = 0, fail = 0;

function test(label, item, shopSlot, expect) {
  let got;
  try {
    got = fn(setup, item, shopSlot);
  } catch (e) {
    console.log(`  ❌ ${label}: 抛异常 ${e.message}`);
    fail++;
    return;
  }
  const ok = got === expect;
  console.log(`  ${ok ? "✅" : "❌"} ${label}: ${JSON.stringify(got)}  ${ok ? "" : "(期望 " + expect + ")"}`);
  ok ? pass++ : fail++;
}

// 有 slot 的：应原样返回
test("普通上衣（有 slot）", setup.clothes.upper[0], "all", "upper");
test("普通下装（有 slot）", setup.clothes.lower[0], "all", "lower");
test("帽子（有 slot）", setup.clothes.head[0], "all", "head");

// 缺 slot 的：应按 index 反查
test("dragonbreath（缺 slot）", setup.clothes.upper[1], "all", "upper");
test("Queen of heart（缺 slot）", setup.clothes.upper[2], "all", "upper");
test("Sweet snow suit（缺 slot）", setup.clothes.upper[3], "all", "upper");
test("Alice's dream（缺 slot）", setup.clothes.upper[4], "all", "upper");
test("acorn（缺 slot）", setup.clothes.upper[5], "all", "upper");
test("Suit for Adventurer（缺 slot）", setup.clothes.upper[6], "all", "upper");

// 指定栏位时：直接返回指定值
test("指定 upper", setup.clothes.upper[1], "upper", "upper");
test("指定 lower", setup.clothes.upper[1], "lower", "lower");

// 完全查不到的：应回退 "upper"
const ghost = mk("不存在的", 9999, "ghost");
test("查不到（回退 upper）", ghost, "all", "upper");

console.log(`\n结果: ${pass} 通过 / ${fail} 失败`);
process.exit(fail === 0 ? 0 : 1);
