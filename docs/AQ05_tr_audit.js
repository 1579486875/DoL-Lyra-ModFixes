/**
 * AQ05：全模组 TweeReplacer findRegex/findString 体检（JS 正则语义）。
 * 对照静态 index（TweeReplacer 之前的 passage 内容），列出：
 *   - 正则以未转义 [ 开头（字符类陷阱）  - 命中次数异常（all=false 却多处命中 / 单次命中很短）
 *   - 命中片段长度 <= 3（几乎肯定是正则写错）
 * 用法: node AQ05_tr_audit.js <index.html> <_mods 目录>
 */
const fs = require("fs");
const path = require("path");
const raw = fs.readFileSync(process.argv[2], "utf8");
const root = process.argv[3];
const unesc = s => s.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, "&");
const P = new Map();
const re = /<tw-passagedata\s+([^>]*)>([\s\S]*?)<\/tw-passagedata>/g;
let m;
while ((m = re.exec(raw)) !== null) {
  const nm = /name="([^"]*)"/.exec(m[1]);
  if (nm) P.set(unesc(nm[1]), unesc(m[2]));
}
const out = [];
for (const d of fs.readdirSync(root)) {
  const bp = path.join(root, d, "boot.json");
  if (!fs.existsSync(bp)) continue;
  let bj;
  try { bj = JSON.parse(fs.readFileSync(bp, "utf8").replace(/^\uFEFF/, "")); } catch (e) { continue; }
  for (const a of bj.addonPlugin || []) {
    if (a.addonName !== "TweeReplacerAddon" || !Array.isArray(a.params)) continue;
    a.params.forEach((p, i) => {
      const body = P.get(p.passage);
      const rec = { mod: bj.name, i, passage: p.passage, all: !!p.all, kind: p.findRegex ? "regex" : "string", flags: [] };
      if (body === undefined) { rec.flags.push("passage 不在 index（可能由模组自身 twee 提供）"); out.push(rec); return; }
      if (p.findRegex) {
        if (/^\[\[|^\[[^\\\]]*\(/.test(p.findRegex)) rec.flags.push("正则以未转义 [ 开头（字符类陷阱）");
        let rx;
        try { rx = new RegExp(p.findRegex, "g" + ((p.regexFlag || "").replace("g", ""))); } catch (e) { rec.flags.push("正则无法编译: " + e.message); out.push(rec); return; }
        const ms = [...body.matchAll(rx)];
        rec.hits = ms.length;
        rec.sample = ms.slice(0, 3).map(x => x[0].slice(0, 80));
        if (ms.length && ms.some(x => x[0].length <= 3)) rec.flags.push("命中片段 ≤3 字符");
        if (!rec.all && ms.length > 1) rec.flags.push("all=false 但命中 " + ms.length + " 处（只替换第一处）");
        if (rec.all && ms.length > 6) rec.flags.push("all=true 命中 " + ms.length + " 处");
      } else if (typeof p.findString === "string") {
        let c = 0, k = -1;
        while ((k = body.indexOf(p.findString, k + 1)) >= 0) c++;
        rec.hits = c;
        if (!rec.all && c > 1) rec.flags.push("all=false 但命中 " + c + " 处");
      }
      out.push(rec);
    });
  }
}
const flagged = out.filter(r => r.flags.length);
console.log(`TweeReplacer 参数 ${out.length} 条；有疑点 ${flagged.length} 条`);
for (const r of flagged) console.log(`  [${r.mod}#${r.i}] ${r.passage} (${r.kind}, all=${r.all}, hits=${r.hits}) ${r.flags.join("；")} ${r.sample ? JSON.stringify(r.sample) : ""}`);
fs.writeFileSync("_aq05.json", JSON.stringify(out, null, 1));
