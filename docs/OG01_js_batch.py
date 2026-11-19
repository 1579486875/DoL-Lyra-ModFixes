"""第 31-33 轮：批量 JS 表达式验证（一次 node 处理全部）。

先导出所有表达式到 JSON，再用一个 node 脚本批量 new Function 验证。
"""
import html
import json
import os
import re
import subprocess
import tempfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
VANILLA = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"

WORK = r"E:\TAML\_dol\work"
EXPR_JSON = os.path.join(WORK, "_exprs.json")
NODE_JS = os.path.join(WORK, "_check_exprs.js")
RESULT_JSON = os.path.join(WORK, "_exprs_result.json")


def load_blocks(path):
    import zipfile
    if path.endswith(".apk"):
        z = zipfile.ZipFile(path)
        raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    else:
        raw = open(path, "rb").read().decode("utf-8", "replace")
    out = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        pn = html.unescape(m.group(1))
        b = html.unescape(m.group(2))
        for pat in (r"/\*.*?\*/", r"<!--.*?-->", r"/%.*?%/"):
            b = re.sub(pat, " ", b, flags=re.S)
        out[pn] = b
    return out


def extract_macros(text, pat):
    out = []
    for m in re.finditer(pat, text):
        i = m.end()
        depth = 1
        while i < len(text) and depth > 0:
            if text.startswith("<<", i):
                depth += 1
                i += 2
            elif text.startswith(">>", i):
                depth -= 1
                i += 2
            else:
                i += 1
        out.append(text[m.end():i - 2])
    return out


KINDS = [
    ("if", r"<<if\b", "cond"),
    ("elseif", r"<<elseif\b", "cond"),
    ("unless", r"<<unless\b", "cond"),
    ("while", r"<<while\b", "cond"),
    ("set", r"<<set\b", "stmt"),
    ("run", r"<<run\b", "stmt"),
    ("print", r"<<print\b", "expr"),
    ("=", r"<<=\s", "expr"),
]


def collect(blocks):
    items = []
    for pn, b in blocks.items():
        for name, pat, kind in KINDS:
            for expr in extract_macros(b, pat):
                if expr.strip():
                    items.append({"pn": pn, "kind": kind, "name": name, "expr": expr})
    return items


def main():
    mb = load_blocks(HTML)
    vb = load_blocks(VANILLA)

    m_items = collect(mb)
    v_items = collect(vb)
    print(f"modded  表达式: {len(m_items)}")
    print(f"vanilla 表达式: {len(v_items)}")

    # 只验证 modded（vanilla 太多，用抽样对照）
    json.dump({"modded": m_items, "vanilla": v_items[::5]},
              open(EXPR_JSON, "w", encoding="utf-8"), ensure_ascii=False)

    NODE_SRC = r"""
const fs = require('fs');
const data = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const out = {};
for (const [label, items] of Object.entries(data)) {
    const errs = [];
    for (const it of items) {
        let src;
        if (it.kind === 'cond') src = 'if (' + it.expr + ') {}';
        else if (it.kind === 'stmt') src = it.expr;
        else src = 'return (' + it.expr + ');';
        try {
            new Function(src);
        } catch (e) {
            errs.push({pn: it.pn, name: it.name, expr: it.expr.slice(0, 180), err: String(e.message)});
        }
    }
    out[label] = {total: items.length, errors: errs};
}
fs.writeFileSync(process.argv[3], JSON.stringify(out, null, 1));
console.log('done');
"""
    open(NODE_JS, "w", encoding="utf-8").write(NODE_SRC)

    r = subprocess.run(["node", NODE_JS, EXPR_JSON, RESULT_JSON],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print("node:", r.stdout.strip(), r.stderr[:300])

    res = json.load(open(RESULT_JSON, encoding="utf-8"))
    for label in ("modded", "vanilla"):
        if label not in res:
            continue
        d = res[label]
        print("\n" + "=" * 94)
        print(f"{label}: {d['total']} 个表达式，语法错误 {len(d['errors'])}")
        print("=" * 94)
        from collections import Counter
        for name, c in Counter(x["name"] for x in d["errors"]).most_common():
            print(f"  <<{name}>>: {c}")
        for x in d["errors"][:20]:
            print(f"\n  [{x['pn']}] <<{x['name']}>>")
            print(f"    expr: {x['expr']!r}")
            print(f"    err : {x['err']}")

    # 归属
    m_bad = {(x["pn"], x["expr"]) for x in res.get("modded", {}).get("errors", [])}
    v_bad = {(x["pn"], x["expr"]) for x in res.get("vanilla", {}).get("errors", [])}
    print("\n" + "=" * 94)
    print(f"modded 独有错误（我引入的）: {len(m_bad - v_bad)}")
    for x in sorted(m_bad - v_bad)[:15]:
        print(f"    {x}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
