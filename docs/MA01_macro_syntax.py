"""补充检查：宏内部的语法正确性（配对检查查不出的那类）。

1) <<if>> / <<elseif>> 表达式里是否含 <<
2) <<set>> / <<run>> / <<=>> / <<print>> 里是否含 <<
3) 所有宏内部括号是否平衡
4) 嵌套宏（宏参数里再套宏）
"""
import html
import re
from collections import Counter

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")

# 逐 passage 处理，去注释
blocks = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
    pn = html.unescape(m.group(1))
    body = html.unescape(m.group(2))
    for pat in (r"/\*.*?\*/", r"<!--.*?-->", r"/%.*?%/"):
        body = re.sub(pat, " ", body, flags=re.S)
    blocks[pn] = body

print("=" * 94)
print("A) 逻辑宏表达式里含 <<")
print("=" * 94)
LOGIC = r"<<(if|elseif|unless|while)\s+([^>]*)>>"
bad_logic = []
for pn, b in blocks.items():
    for m in re.finditer(LOGIC, b):
        expr = m.group(2)
        if "<<" in expr:
            bad_logic.append((pn, m.group(1), expr[:150]))
print(f"  命中 {len(bad_logic)} 处")
for x in bad_logic[:15]:
    print(f"    [{x[0]}] <<{x[1]} {x[2]!r}")

print("\n" + "=" * 94)
print("B) 赋值/输出宏里含 <<")
print("=" * 94)
ASSIGN = r"<<(set|run|print|=)\s+([^>]*)>>"
bad_assign = []
for pn, b in blocks.items():
    for m in re.finditer(ASSIGN, b):
        expr = m.group(2)
        # <<= >> 里可以含 << 吗？不行
        if "<<" in expr:
            bad_assign.append((pn, m.group(1), expr[:150]))
print(f"  命中 {len(bad_assign)} 处")
for x in bad_assign[:15]:
    print(f"    [{x[0]}] <<{x[1]} {x[2]!r}")

print("\n" + "=" * 94)
print("C) 宏内部括号平衡")
print("=" * 94)
PAIR = {"(": ")", "[": "]", "{": "}"}
bad_paren = []
for pn, b in blocks.items():
    for m in re.finditer(r"<<(if|elseif|set|run|print|=)\s+([^>]*)>>", b):
        expr = m.group(2)
        # 去掉字符串字面量
        e = re.sub(r'"[^"]*"', '""', expr)
        e = re.sub(r"'[^']*'", "''", e)
        e = re.sub(r"`[^`]*`", "``", e)
        stack = []
        ok = True
        for ch in e:
            if ch in PAIR:
                stack.append(PAIR[ch])
            elif ch in PAIR.values():
                if not stack or stack.pop() != ch:
                    ok = False
                    break
        if not ok or stack:
            bad_paren.append((pn, m.group(1), expr[:140]))
print(f"  括号不平衡: {len(bad_paren)} 处")
for x in bad_paren[:15]:
    print(f"    [{x[0]}] <<{x[1]} {x[2]!r}")

print("\n" + "=" * 94)
print("D) 嵌套宏（宏参数里再套宏）")
print("=" * 94)
nested = Counter()
samples = {}
for pn, b in blocks.items():
    for m in re.finditer(r"<<([a-zA-Z][\w\-]*)\s+([^>]*<<[^>]*)>>", b):
        name = m.group(1)
        nested[name] += 1
        samples.setdefault(name, (pn, m.group(0)[:160]))
print(f"  含嵌套参数的宏: {len(nested)} 种 / {sum(nested.values())} 处")
for name, c in nested.most_common(10):
    pn, s = samples[name]
    print(f"    {c:>3}  <<{name}>>  [{pn}]")
    print(f"         {s!r}")

print("\n" + "=" * 94)
print("E) 我注入的宏定义是否语法正确")
print("=" * 94)
for kw in ("NPC_CN_NAME", "NPC_CN_TYPE", "BODYPARTS_CN_NAME"):
    m = re.search(r'<<widget\s+"' + kw + r'"\s*>>(.*?)<</widget>>', "\n".join(blocks.values()), re.S)
    if m:
        body = m.group(1)
        print(f"  {kw}: {body.strip()[:120]!r}")
    else:
        print(f"  {kw}: ❌ 未找到")
