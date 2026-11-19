"""第 37-39 轮：补全 SugarCube 语法转换后重新验证。

补充：
  eq  -> ===
  neq -> !==
  ndef X  (前缀) -> (X === undefined)
  def X   (前缀) -> (X !== undefined)
"""
import html
import json
import os
import re
import subprocess

WORK = r"E:\TAML\_dol\work"
EXPR_JSON = os.path.join(WORK, "_exprs.json")
NODE_JS = os.path.join(WORK, "_check_exprs3.js")
RESULT_JSON = os.path.join(WORK, "_exprs_result3.json")

NODE_SRC = r"""
const fs = require('fs');
const data = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));

function toJS(expr) {
    let s = expr;
    // 保护字符串
    const strs = [];
    s = s.replace(/`(?:[^`\\]|\\.)*`|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'/g, m => {
        strs.push(m);
        return '\u0000' + (strs.length - 1) + '\u0000';
    });
    // 前缀形式 def / ndef（整段表达式开头）
    s = s.replace(/^\s*ndef\s+([\w.$\[\]'"`]+)\s*$/, '(($1) === undefined)');
    s = s.replace(/^\s*def\s+([\w.$\[\]'"`]+)\s*$/, '(($1) !== undefined)');
    // 中缀运算符
    const rules = [
        [/\bis\s+not\b/g, '!=='],
        [/\bisnot\b/g, '!=='],
        [/\bis\b/g, '==='],
        [/\bneq\b/g, '!=='],
        [/\beq\b/g, '==='],
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
    s = s.replace(/\u0000(\d+)\u0000/g, (_, i) => strs[+i]);
    return s;
}

const out = {};
for (const [label, items] of Object.entries(data)) {
    const errs = [];
    for (const it of items) {
        const js = toJS(it.expr);
        let src;
        if (it.kind === 'cond') src = 'if (' + js + ') {}';
        else if (it.kind === 'stmt') src = js;
        else src = 'return (' + js + ');';
        try { new Function(src); }
        catch (e) { errs.push({pn: it.pn, name: it.name, expr: it.expr.slice(0, 180), js: js.slice(0, 180), err: String(e.message)}); }
    }
    out[label] = {total: items.length, errors: errs};
}
fs.writeFileSync(process.argv[3], JSON.stringify(out, null, 1));
console.log('done');
"""


def main():
    open(NODE_JS, "w", encoding="utf-8").write(NODE_SRC)
    r = subprocess.run(["node", NODE_JS, EXPR_JSON, RESULT_JSON],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print("node:", r.stdout.strip(), r.stderr[:200])

    res = json.load(open(RESULT_JSON, encoding="utf-8"))
    from collections import Counter

    for label in ("modded", "vanilla"):
        if label not in res:
            continue
        d = res[label]
        pct = len(d["errors"]) / max(1, d["total"]) * 100
        print("\n" + "=" * 94)
        print(f"{label}: {d['total']} 个表达式，语法错误 {len(d['errors'])} ({pct:.3f}%)")
        print("=" * 94)
        for name, c in Counter(x["name"] for x in d["errors"]).most_common():
            print(f"  <<{name}>>: {c}")

    m_bad = {(x["pn"], x["expr"]) for x in res.get("modded", {}).get("errors", [])}
    v_bad = {(x["pn"], x["expr"]) for x in res.get("vanilla", {}).get("errors", [])}
    print("\n" + "=" * 94)
    print(f"modded 独有错误（我引入的）: {len(m_bad - v_bad)}")
    print("=" * 94)
    for x in sorted(m_bad - v_bad)[:25]:
        print(f"    {x}")

    # 打印剩余错误样本
    print("\n" + "=" * 94)
    print("modded 剩余错误样本（前 20）")
    print("=" * 94)
    for x in res.get("modded", {}).get("errors", [])[:20]:
        print(f"\n  [{x['pn']}] <<{x['name']}>>")
        print(f"    expr: {x['expr']!r}")
        print(f"    js  : {x['js']!r}")
        print(f"    err : {x['err']}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
