"""第 1-6 轮：用 Node 实际编译 <<if>> / <<set>> 里的表达式。

SugarCube 的 <<if>> 条件、<<set>> 的右值都是在 JS 引擎里 eval 的。
静态正则只能查结构，只有真编译才能查出「语法错误」。

做法：
  把每个表达式包成 `function(){ return (EXPR); }` 交给 node --check
  对 <<set>> 用 `function(){ EXPR; }`
"""
import html
import json
import os
import re
import subprocess
import tempfile
from collections import Counter

HTML = r"E:\TAML\_dol\work\index_modded6.html"
VANILLA = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"

TMP = os.path.join(tempfile.gettempdir(), "dsh_expr_check.js")


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


def extract_macros(text, name_pat):
    """用配对大括号扫描提取宏的完整参数。"""
    out = []
    for m in re.finditer(name_pat, text):
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
        out.append((m.start(), text[m.end():i - 2]))
    return out


def node_check(src):
    open(TMP, "w", encoding="utf-8").write(src)
    r = subprocess.run(["node", "--check", TMP], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    return r.returncode == 0, (r.stderr or "")[:300]


def check_blocks(blocks, label):
    errs = []
    total = 0
    for pn, b in blocks.items():
        # <<if>> / <<elseif>> / <<unless>> / <<while>>
        for name, pat in (("if", r"<<if\b"), ("elseif", r"<<elseif\b"),
                          ("unless", r"<<unless\b"), ("while", r"<<while\b")):
            for pos, expr in extract_macros(b, pat):
                if not expr.strip():
                    continue
                total += 1
                ok, err = node_check("function f(){ if (" + expr + ") {} }")
                if not ok:
                    errs.append((pn, name, expr[:160], err))
        # <<set>> / <<run>>
        for name, pat in (("set", r"<<set\b"), ("run", r"<<run\b")):
            for pos, expr in extract_macros(b, pat):
                if not expr.strip():
                    continue
                total += 1
                ok, err = node_check("function f(){" + expr + "}")
                if not ok:
                    errs.append((pn, name, expr[:160], err))
        # <<= / <<print>>
        for name, pat in (("=", r"<<=\s"), ("print", r"<<print\b")):
            for pos, expr in extract_macros(b, pat):
                if not expr.strip():
                    continue
                total += 1
                ok, err = node_check("function f(){ return (" + expr + "); }")
                if not ok:
                    errs.append((pn, name, expr[:160], err))
    return total, errs


mb = load_blocks(HTML)
vb = load_blocks(VANILLA)

print("=" * 94)
print("第 1-6 轮：JS 表达式真实编译验证")
print("=" * 94)

mt, me = check_blocks(mb, "modded")
print(f"  modded : 检查 {mt} 个表达式，语法错误 {len(me)}")

print("\n  按宏类型统计错误：")
for name, c in Counter(x[1] for x in me).most_common():
    print(f"    <<{name}>>: {c}")

print("\n  前 25 个错误：")
for pn, name, expr, err in me[:25]:
    print(f"\n  [{pn}] <<{name}>>")
    print(f"    expr: {expr!r}")
    print(f"    err : {err.splitlines()[-1] if err else ''}")

print("\n" + "=" * 94)
print("  vanilla 基线对照（抽样同样数量）")
print("=" * 94)
# vanilla 太大，只查一部分 passage
sample = dict(list(vb.items())[:2000])
vt, ve = check_blocks(sample, "vanilla-sample")
print(f"  vanilla 抽样: 检查 {vt} 个表达式，语法错误 {len(ve)}")
for pn, name, expr, err in ve[:8]:
    print(f"    [{pn}] <<{name}>> {expr[:90]!r}")
