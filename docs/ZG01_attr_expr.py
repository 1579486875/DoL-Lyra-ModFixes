"""精确查「SugarCube 属性表达式」（@class / @src / @style / @title 等）里的中文。

这些属性的值是 JS 表达式，含中文就是非法（除非在字符串字面量里）。
"""
import html as H
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
CJK = re.compile(r"[\u4e00-\u9fff]")

data = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(data)

print("=" * 90)
print("SugarCube 属性表达式（@xxx=\"...\"）里的中文")
print("=" * 90)

hits = []
for m in re.finditer(r'@([\w:-]+)="([^"]{0,400})"', g):
    attr, expr = m.group(1), m.group(2)
    if not CJK.search(expr):
        continue
    # 去掉字符串字面量后再看
    base = re.sub(r'"(?:[^"\\]|\\.)*"', '""', expr)
    base = re.sub(r"'(?:[^'\\]|\\.)*'", "''", base)
    if CJK.search(base):
        hits.append((attr, expr, m.start()))

print(f"共 {len(hits)} 处")
for attr, expr, pos in hits[:20]:
    print(f"\n  @{attr}=\"{expr[:120]}\"")
    print(f"    {g[max(0,pos-100):pos+180]!r}")
