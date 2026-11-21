/**
 * T03：用游戏引擎自己的 Scripting.parse，对每个宏表达式做「解析后编译」检查。
 *
 * 用法: node --max-old-space-size=8192 T03_sc_compile_all.js <index.html> [out.json]
 *
 * 原理：SugarCube 会把 _x / $x / to / is ... 词元改写成 State.temporary.x 等，
 * 改写后的代码才是真正交给 eval 的东西。本工具从 index 里抠出引擎的 parse 实现，
 * 原样执行，然后 new Function() 编译 —— 编译失败 = 游戏里必然红字。
 */
const fs = require("fs");

const FILE = process.argv[2];
const OUT = process.argv[3] || null;
const raw = fs.readFileSync(FILE, "utf8");

// ---------- 1. 抠出引擎 parse ----------
const ps = raw.indexOf("const parse=(()=>{const tokenTable");
const pe = raw.indexOf("return parse})()", ps);
if (ps < 0 || pe < 0) { console.error("找不到引擎 parse"); process.exit(2); }
const parseSrc = raw.slice(ps, pe + "return parse})()".length);
Object.defineProperty(String.prototype, "splice", {
  configurable: true, writable: true,
  value(startAt, delCount, replacement) {
    const length = this.length >>> 0;
    if (length === 0) return "";
    let start = Number(startAt);
    if (Number.isSafeInteger(start)) { if (start < 0) { start += length; if (start < 0) start = 0; } } else start = 0;
    if (start > length) start = length;
    let count = Number(delCount);
    if (!Number.isSafeInteger(count) || count < 0) count = 0;
    let res = this.slice(0, start);
    if (replacement !== undefined) res += replacement;
    if (start + count < length) res += this.slice(start + count);
    return res;
  },
});
const Util = { toEnum: o => Object.freeze(Object.assign(Object.create(null), o)) };
const Patterns = { variable: "[$_=][$A-Z_a-z][$0-9A-Z_a-z]*" };
const parse = new Function("Util", "Patterns", parseSrc + ";return parse;")(Util, Patterns);

// ---------- 2. 取 passage ----------
const unesc = s => s.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"')
  .replace(/&#39;/g, "'").replace(/&amp;/g, "&");
const PASS = [];
const reP = /<tw-passagedata\s+([^>]*)>([\s\S]*?)<\/tw-passagedata>/g;
let m;
while ((m = reP.exec(raw)) !== null) {
  const attrs = m[1];
  const nm = /name="([^"]*)"/.exec(attrs);
  const tg = /tags="([^"]*)"/.exec(attrs);
  PASS.push({ name: nm ? unesc(nm[1]) : "?", tags: tg ? tg[1] : "", body: unesc(m[2]) });
}

// ---------- 2b. --twee-dir <目录>：改为扫描模组的 .twee 文件（引擎 parse 仍取自 index）----------
const TI = process.argv.indexOf("--twee-dir");
if (TI > 0) {
  const path = require("path");
  const root = process.argv[TI + 1];
  PASS.length = 0;
  const walk = d => {
    for (const f of fs.readdirSync(d)) {
      const p = path.join(d, f);
      if (fs.statSync(p).isDirectory()) walk(p);
      else if (/\.twee$/i.test(f)) {
        const src = fs.readFileSync(p, "utf8").replace(/\r\n/g, "\n");
        const parts = src.split(/^::[ \t]*/m);
        for (const part of parts.slice(1)) {
          const nl = part.indexOf("\n");
          const head = nl < 0 ? part : part.slice(0, nl);
          const body = nl < 0 ? "" : part.slice(nl + 1);
          const hm = /^(.*?)(?:\s*\[([^\]]*)\])?(?:\s*\{.*\})?\s*$/.exec(head);
          PASS.push({ name: path.relative(root, p) + " :: " + (hm ? hm[1].trim() : head), tags: hm && hm[2] ? hm[2] : "", body });
        }
      }
    }
  };
  walk(root);
}

// ---------- 3. 去掉不参与宏解析的区域（注释 / nowiki / <<script>>）----------
function blank(s, re) { return s.replace(re, x => x.replace(/[^\n]/g, " ")); }
function prep(body) {
  let s = body;
  s = blank(s, /\/\*[\s\S]*?\*\//g);
  s = blank(s, /\/%[\s\S]*?%\//g);
  s = blank(s, /<!--[\s\S]*?-->/g);
  s = blank(s, /"""[\s\S]*?"""/g);
  s = blank(s, /<nowiki>[\s\S]*?<\/nowiki>/gi);
  s = blank(s, /\{\{\{[\s\S]*?\}\}\}/g);
  s = blank(s, /<<script>>[\s\S]*?<<\/script>>/g);
  return s;
}

// ---------- 4. 宏参数切分：找配对的 >>（跳过引号/反引号/[[ ]]）----------
function macroArgsEnd(s, i) {
  let q = null;
  let sq = 0;
  for (; i < s.length; i++) {
    const c = s[i];
    if (q) {
      if (c === "\\") { i++; continue; }
      if (c === q) q = null;
      continue;
    }
    if (c === '"' || c === "'" || c === "`") { q = c; continue; }
    if (c === "[" && s[i + 1] === "[") { sq++; i++; continue; }
    if (c === "]" && s[i + 1] === "]" && sq > 0) { sq--; i++; continue; }
    if (c === ">" && s[i + 1] === ">" && sq === 0) return i;
  }
  return -1;
}

const EXPR = new Set(["if", "elseif", "print", "=", "-", "switch"]);
const STMT = new Set(["set", "run"]);
const errors = [];
let checked = 0;

function tryCompile(kind, code) {
  let p;
  try { p = parse(code); } catch (e) { return "parse: " + e.message; }
  try {
    // 引擎用 eval(code) 执行 if/print/set/run —— 按「程序」语义编译，最贴近 eval
    if (kind === "for3") new Function("for(" + p + "\n){}");
    else new Function(p + "\n;");
    return null;
  } catch (e) { return e.name + ": " + e.message; }
}

function tryExpr(code) {
  // 反引号参数 / @属性：表达式语境；先按表达式编译，不行再按程序编译
  let p;
  try { p = parse(code); } catch (e) { return "parse: " + e.message; }
  try { new Function("return (" + p + "\n);"); return null; } catch (e1) {
    try { new Function(p + "\n;"); return null; } catch (e2) { return e1.name + ": " + e1.message; }
  }
}

// 切出反引号参数（宏参数里的 `...`，跳过普通引号串）
function backtickArgs(args) {
  const out = [];
  let q = null, st = -1;
  for (let i = 0; i < args.length; i++) {
    const c = args[i];
    if (q) {
      if (c === "\\") { i++; continue; }
      if (c === q) { if (q === "`") out.push(args.slice(st + 1, i)); q = null; }
      continue;
    }
    if (c === '"' || c === "'" || c === "`") { q = c; st = i; }
  }
  return out;
}

const SKIP_BT = new Set([...EXPR, ...STMT, "for", "script", "case", "widget", "silently", "nobr"]);

function scanText(srcName, body, sink) {
  const s = prep(body);
  const lineOf = i => s.slice(0, i).split("\n").length;
  const re = /<<([A-Za-z][\w-]*|=|-)(?=[\s>])/g;
  let mm;
  while ((mm = re.exec(s)) !== null) {
    const name = mm[1];
    const a0 = mm.index + 2 + name.length;
    const e = macroArgsEnd(s, a0);
    if (e < 0) continue;
    // 宏标签会吞掉到 >> 为止的全部参数 —— 参数里（字符串中）的 <<...>> 不是宏，跳过
    re.lastIndex = e + 2;
    const args = s.slice(a0, e).trim();
    if (!args) continue;
    let err = null;
    let kind = name;
    if (EXPR.has(name) || STMT.has(name) || name === "for") {
      checked++;
      if (EXPR.has(name)) err = tryCompile("expr", args);
      else if (STMT.has(name)) err = tryCompile("stmt", args);
      else {
        const r = /^\s*(?:(_\w+|\$\w+)\s*(?:,\s*(_\w+|\$\w+)\s*)?)?range\s+([\s\S]+)$/.exec(args);
        // 引擎 handleForRange：rangeExp 以 { 开头时包一层括号再 eval（对象字面量）
        if (r) err = tryCompile("expr", r[3].trim()[0] === "{" ? "(" + r[3] + ")" : r[3]);
        else if (args.includes(";")) err = tryCompile("for3", args);
        else err = tryCompile("expr", args);
      }
      if (err) sink.push({ passage: srcName, macro: kind, line: lineOf(mm.index), args: args.slice(0, 400), err, full: body.slice(mm.index, e + 2) });
    } else if (!SKIP_BT.has(name)) {
      // 其它宏（含 widget 调用）的反引号参数会被求值
      for (const bt of backtickArgs(args)) {
        checked++;
        // DoL 的宏参数里反引号段按「模板字面量」求值（`Put your ${...}`）
        const er = tryExpr("`" + bt + "`");
        if (er) sink.push({ passage: srcName, macro: name + "`", line: lineOf(mm.index), args: bt.slice(0, 400), err: er });
      }
      // [[文本|目标][setter]] 形式的 setter
      const rl = /\[\[[^\]]*\]\[([^\]]+)\]\]/g;
      let lm;
      while ((lm = rl.exec(args)) !== null) {
        checked++;
        const er = tryCompile("stmt", lm[1]);
        if (er) sink.push({ passage: srcName, macro: name + "[setter]", line: lineOf(mm.index), args: lm[1].slice(0, 400), err: er });
      }
    }
  }
  // 正文里的 [[...][setter]] 链接
  const rl2 = /\[\[[^\]\n]*\]\[([^\]\n]+)\]\]/g;
  let lm2;
  while ((lm2 = rl2.exec(s)) !== null) {
    checked++;
    const er = tryCompile("stmt", lm2[1]);
    if (er) sink.push({ passage: srcName, macro: "[[setter]]", line: lineOf(lm2.index), args: lm2[1].slice(0, 400), err: er });
  }
  // HTML 属性指令 @attr="expr"
  const ra = /<[A-Za-z][\w-]*\s[^<>]*?@([\w-]+)\s*=\s*"([^"]*)"/g;
  let am;
  while ((am = ra.exec(s)) !== null) {
    checked++;
    const er = tryExpr(am[2]);
    if (er) sink.push({ passage: srcName, macro: "@" + am[1], line: lineOf(am.index), args: am[2].slice(0, 400), err: er });
  }
}

module.exports = { parse, scanText, prep };

if (require.main === module) {
  for (const P of PASS) {
    if (/\b(script|stylesheet|Twine\.private)\b/.test(P.tags)) continue;
    scanText(P.name, P.body, errors);
  }
}

console.log(`passage ${PASS.length}  已检查宏 ${checked}  编译失败 ${errors.length}`);
const byP = {};
for (const e of errors) byP[e.passage] = (byP[e.passage] || 0) + 1;
console.log("按 passage（前 30）:", JSON.stringify(Object.entries(byP).sort((a, b) => b[1] - a[1]).slice(0, 30)));
if (OUT) fs.writeFileSync(OUT, JSON.stringify(errors, null, 1), "utf8");
