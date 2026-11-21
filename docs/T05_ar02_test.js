// T05：用 TweeReplacer 同款逻辑，把 AR02 改后的 4 条补丁套到「运行时（未打补丁）」的 passage 上验证
const fs = require("fs");
const path = require("path");
const T = process.env.TEMP;
const rt = new Map();
for (const line of fs.readFileSync(process.argv[2], "utf8").split("\n")) {
  if (!line.trim()) continue;
  const [t, tg, body] = JSON.parse(line);
  rt.set(t, body);
}
const dr = JSON.parse(fs.readFileSync(path.join(T, "ar02/dr/boot.json"), "utf8"));
const ds = JSON.parse(fs.readFileSync(path.join(T, "ar02/ds/boot.json"), "utf8"));
const files = { "game/base-combat/bookSims_4.txt": fs.readFileSync(path.join(T, "ar02/ds/bookSims_4.txt"), "utf8"),
                "game/robin-daily/oceanBreeze.txt": fs.readFileSync(path.join(T, "ar02/dr/oceanBreeze.txt"), "utf8") };
let pass = 0, fail = 0;
const ok = (n, c, d) => { if (c) { pass++; console.log("  ✅ " + n); } else { fail++; console.log("  ❌ " + n + (d ? "  " + d : "")); } };
function apply(p) {
  let content = rt.get(p.passage);
  if (content === undefined) return { err: "no passage" };
  const rep = p.replaceFile ? files[p.replaceFile] : p.replace;
  if (rep === undefined) return { err: "no replace " + p.replaceFile };
  if (p.findString) {
    if (!content.includes(p.findString)) return { err: "findString miss" };
    const n = content.split(p.findString).length - 1;
    return { out: p.all ? content.replaceAll(p.findString, rep) : content.replace(p.findString, rep), n };
  }
  const flag = p.all ? (p.regexFlag ?? "g") : (p.regexFlag ?? undefined);
  const rx = new RegExp(p.findRegex, flag);
  if (content.search(rx) < 0) return { err: "findRegex miss" };
  return { out: p.all ? content.replaceAll(rx, rep) : content.replace(rx, rep), n: (content.match(new RegExp(p.findRegex, "g")) || []).length };
}
const pick = (bj, pred) => bj.addonPlugin.filter(a => a.addonName === "TweeReplacerAddon").flatMap(a => a.params).find(pred);
// DoLSims fallenTransform
const p1 = pick(ds, p => p.passage === "Transformation Widgets" && /fallenTransform/.test(p.findRegex || ""));
const r1 = apply(p1);
ok("fallenTransform 命中", !r1.err, r1.err);
if (r1.out) {
  const seg = r1.out.slice(r1.out.indexOf('<<widget "fallenTransform">>'), r1.out.indexOf('<<widget "fallenTransform">>') + 260);
  ok("保留 maplebirch 外层 <<if not …>>", seg.includes("<<if not ($settings.transformDivineEnabled"), seg.slice(0, 120));
  ok("插入 DoLSims 书本特性分支", seg.includes("$citylibrarybook_14_4_trait is 1"));
  const w = r1.out.slice(r1.out.indexOf('<<widget "fallenTransform">>'));
  const body = w.slice(0, w.indexOf("<</widget>>"));
  const o = (body.match(/<<if\b/g) || []).length, c = (body.match(/<<\/if>>/g) || []).length;
  ok("fallenTransform 内 <<if>>/<</if>> 配平 " + o + "/" + c, o === c);
}
// DomRobin
for (const [nm, pred, must] of [
  ["Bailey's Office", p => p.passage === "Bailey's Office" && /robinpaid/.test(p.findString || ""), '<<if !$robinPaySelfTalked and $robinpaid isnot 1 and $robindebtknown is 1 and !maplebirch.get("Finance")'],
  ["robinpay", p => p.passage === "Widgets Robin" && /robinpay/.test(p.findString || ""), '<<if !$robinPaySelfTalked and $robinpaid isnot 1 and !maplebirch.get("Finance").orphanage.robinFree>>'],
  ["Ocean Breeze", p => p.passage === "Ocean Breeze" && /canPay\\\(300/.test(p.findRegex || ""), 'maplebirch.get("Finance").canPay(300, "cafe")>>'],
]) {
  const p = pick(dr, pred);
  if (!p) { ok(nm + " 参数存在", false); continue; }
  const r = apply(p);
  ok(nm + " 命中（" + (r.n || 0) + " 处）", !r.err && r.n === 1, r.err);
  if (r.out) ok(nm + " 结果包含预期文本", r.out.includes(must), must);
  if (nm === "Ocean Breeze" && r.out) ok("Ocean Breeze 插入罗宾买酒选项", r.out.includes("为罗宾购买_wineType"));
}
console.log(`\n结果: ${pass} 通过 / ${fail} 失败`);
process.exit(fail ? 1 : 0);
