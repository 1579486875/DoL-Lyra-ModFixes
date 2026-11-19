"""第 34-36 轮：SugarCube 语法转 JS 后再验证。

SugarCube 的宏参数是它自己的表达式语言：
  <<set $x to 1>>          -> $x = 1
  <<if $x is 1>>           -> if ($x === 1)
  <<if $x isnot 1>>        -> if ($x !== 1)
  <<if $x gt 1>>           -> if ($x > 1)
  <<if a and b>>           -> if (a && b)
  <<if not a>>             -> if (!a)
  <<if $x def>>            -> if ($x !== undefined)

先转换再丢给 new Function，才是正确的验证。
"""
import html
import json
import os
import re
import subprocess

WORK = r"E:\TAML\_dol\work"
EXPR_JSON = os.path.join(WORK, "_exprs.json")
NODE_JS = os.path.join(WORK, "_check_exprs2.js")
RESULT_JSON = os.path.join(WORK, "_exprs_result2.json")

# SugarCube -> JS 转换（顺序重要）
CONV = [
    (r"\bis\s+not\b", "!=="),
    (r"\bisnot\b", "!=="),
    (r"\bis\b", "==="),
    (r"\bdef\b", "!== undefined"),
    (r"\bndef\b", "=== undefined"),
    (r"\bgte\b", ">="),
    (r"\blte\b", "<="),
    (r"\bgt\b", ">"),
    (r"\blt\b", "<"),
    (r"\band\b", "&&"),
    (r"\bor\b", "||"),
    (r"\bnot\b", "!"),
    (r"\bto\b", "="),
]

NODE_SRC = r"""
const fs = require('fs');
const data = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));

function toJS(expr, kind) {
    let s = expr;
    // 先保护字符串字面量
    const strings = [];
    s = s.replace(/`[^`]*`|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'/g, m => {
        strings.push(m);
        return '\u0000' + (strings.length - 1) + '\u0000';
    });
    const rules = [
        [/\bis\s+not\b/g, '!=='],
        [/\bisnot\b/g, '!=='],
        [/\bis\b/g, '==='],
        [/\bndef\b/g, '=== undefined'],
        [/\bdef\b/g, '!== undefined'],
        [/\bgte\b/g, '>='],
        [/\blte\b/g, '<='],
        [/\bgt\b/g, '>'],
        [/\blt\b/g, '<'],
        [/\band\b/g, '&&'],
        [/\bor\b/g, '||'],
        [/\bnot\b/g, '!'],
        [/\bto\b/g, '='],
    ];
    for (const [re, rep] of rules) s = s.replace(re, rep);
    s = s.replace(/\u0000(\d+)\u0000/g, (_, i) => strings[+i]);
    return s;
}

const out = {};
for (const [label, items] of Object.entries(data)) {
    const errs = [];
    for (const it of items) {
        const js = toJS(it.expr, it.kind);
        let src;
        if (it.kind === 'cond') src = 'if (' + js + ') {}';
        else if (it.kind === 'stmt') src = js;
        else src = 'return (' + js + ');';
        try {
            new Function(src);
        } catch (e) {
            errs.push({pn: it.pn, name: it.name, expr: it.expr.slice(0, 180), js: js.slice(0, 180), err: String(e.message)});
        }
    }
    out[label] = {total: items.length, errors: errs};
}
fs.writeFileSync(process.argv[3], JSON.stringify(out, null, 1));
console.log('done');
"""


def main():
    if not os.path.exists(EXPR_JSON):
        print("❌ 先跑 OG01 生成 _exprs.json")
        return 1

    open(NODE_JS, "w", encoding="utf-8").write(NODE_SRC)
    r = subprocess.run(["node", NODE_JS, EXPR_JSON, RESULT_JSON],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print("node:", r.stdout.strip(), r.stderr[:300])

    res = json.load(open(RESULT_JSON, encoding="utf-8"))
    for label in ("modded", "vanilla"):
        if label not in res:
            continue
        d = res[label]
        pct = len(d["errors"]) / max(1, d["total"]) * 100
        print("\n" + "=" * 94)
        print(f"{label}: {d['total']} 个表达式，语法错误 {len(d['errors'])} ({pct:.2f}%)")
        print("=" * 94)
        from collections import Counter
        for name, c in Counter(x["name"] for x in d["errors"]).most_common():
            print(f"  <<{name}>>: {c}")
        for x in d["errors"][:15]:
            print(f"\n  [{x['pn']}] <<{x['name']}>>")
            print(f"    expr: {x['expr']!r}")
            print(f"    js  : {x['js']!r}")
            print(f"    err : {x['err']}")

    m_bad = {(x["pn"], x["expr"]) for x in res.get("modded", {}).get("errors", [])}
    v_bad = {(x["pn"], x["expr"]) for x in res.get("vanilla", {}).get("errors", [])}
    print("\n" + "=" * 94)
    print(f"modded 独有错误: {len(m_bad - v_bad)}")
    print("=" * 94)
    for x in sorted(m_bad - v_bad)[:20]:
        print(f"    {x}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
