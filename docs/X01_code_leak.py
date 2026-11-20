"""X01（第6轮）：扫「正文里的代码泄漏」。

上轮修了 setup.colourName(.colour)，同类可能还有：
  1. $变量.属性  直接出现在正文（没被 <<print>> 包）
  2. _临时变量   同上
  3. undefined / NaN / null / Infinity 出现在正文
  4. &lt;&lt; / &amp;lt; 双重转义残留
  5. <<宏名>> 没被解析（字面显示）
"""
import html as H
import json
import re
from collections import Counter

raw = open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace")
g = H.unescape(raw)


def in_macro(text, pos):
    """判断 pos 是否在 << >> 里"""
    pre = text[max(0, pos - 500):pos]
    return pre.rfind("<<") > pre.rfind(">>")


def has_cn_near(text, pos, span=40):
    ctx = text[max(0, pos - span):pos + span]
    return bool(re.search(r"[\u4e00-\u9fff]", ctx))


print("=" * 95)
print("1. 正文里的 $变量.属性（没被 <<print>> 包）")
print("=" * 95)
n1 = 0
hits1 = []
for m in re.finditer(r"\$([A-Za-z_][A-Za-z0-9_]*\.[A-Za-z0-9_.]+)", g):
    if in_macro(g, m.start()):
        continue
    if not has_cn_near(g, m.start()):
        continue
    n1 += 1
    if len(hits1) < 25:
        hits1.append((m.start(), m.group(0), g[max(0, m.start() - 70):m.start() + 90]))

print(f"  共 {n1} 处")
for pos, v, ctx in hits1:
    print(f"  @{pos}  {v!r}")
    print(f"    {ctx!r}")

print("\n" + "=" * 95)
print("2. 正文里的 _临时变量（没被 <<print>> 包）")
print("=" * 95)
n2 = 0
hits2 = []
for m in re.finditer(r"(?<![A-Za-z0-9_$])_([a-z][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)*)", g):
    if in_macro(g, m.start()):
        continue
    if not has_cn_near(g, m.start()):
        continue
    v = m.group(0)
    # 排除标签属性 / CSS
    pre = g[max(0, m.start() - 80):m.start()]
    if pre.rfind("<") > pre.rfind(">"):
        continue
    if pre and pre[-1] in ".=({[,;:+*/<>!&|?~^%$-":
        continue
    n2 += 1
    if len(hits2) < 25:
        hits2.append((m.start(), v, g[max(0, m.start() - 70):m.start() + 90]))

print(f"  共 {n2} 处")
for pos, v, ctx in hits2:
    print(f"  @{pos}  {v!r}")
    print(f"    {ctx!r}")

print("\n" + "=" * 95)
print("3. undefined / NaN / null / Infinity 出现在正文")
print("=" * 95)
n3 = 0
hits3 = []
for m in re.finditer(r"\b(undefined|NaN|Infinity)\b", g):
    if in_macro(g, m.start()):
        continue
    pre = g[max(0, m.start() - 100):m.start()]
    if pre.rfind("<") > pre.rfind(">"):
        continue
    # JS 上下文排除
    if re.search(r"typeof|===\s*$|\?\?|\|\||&&", pre[-40:]):
        continue
    if not has_cn_near(g, m.start(), 60):
        continue
    n3 += 1
    if len(hits3) < 20:
        hits3.append((m.start(), m.group(0), g[max(0, m.start() - 80):m.start() + 100]))

print(f"  共 {n3} 处")
for pos, v, ctx in hits3:
    print(f"  @{pos}  {v!r}")
    print(f"    {ctx!r}")

print("\n" + "=" * 95)
print("4. 双重转义残留 &lt;&lt; / &amp;lt;")
print("=" * 95)
n4 = len(re.findall(r"&amp;lt;|&amp;gt;", raw))
n4b = len(re.findall(r"&amp;amp;", raw))
print(f"  &amp;lt; / &amp;gt;: {n4}")
print(f"  &amp;amp;: {n4b}")
for m in list(re.finditer(r"&amp;lt;", raw))[:5]:
    print(f"    @{m.start()}: {raw[max(0,m.start()-60):m.start()+100]!r}")

print("\n" + "=" * 95)
print("汇总")
print("=" * 95)
print(f"  $变量.属性 泄漏:  {n1}")
print(f"  _临时变量 泄漏:   {n2}")
print(f"  undefined/NaN:    {n3}")
print(f"  &amp;lt; 残留:     {n4}")

with open(r"E:\TAML\_dol\work\_code_leak.json", "w", encoding="utf-8") as f:
    json.dump({"dollar": hits1, "temp": hits2, "undef": hits3}, f, ensure_ascii=False, indent=1)
print("已保存 _code_leak.json")
