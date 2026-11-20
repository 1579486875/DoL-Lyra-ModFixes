"""X02：精确找「明显异常」的变量泄漏 —— 排除正常求值。

SugarCube 里 $var / _var 在正文里会被 Wikifier 求值，所以以下都正常：
  「你的$worn.genitals.cn_name_cap」       ← 正常
  「<<for _item range ...>>..._item.name」  ← 正常

异常的是：
  A. 变量名旁边有空格（说明是被拼接进来的）
  B. 变量名是内部名（_output/_result/_temp/_args）
  C. undefined / NaN 出现在正文
"""
import html as H
import json
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))


def in_macro(text, pos):
    pre = text[max(0, pos - 500):pos]
    return pre.rfind("<<") > pre.rfind(">>")


print("=" * 95)
print("1. 变量名前后有空格（被拼接进来的迹象）")
print("=" * 95)
n1 = 0
for m in re.finditer(r"(?<=[\u4e00-\u9fff])\s(\$[A-Za-z_][A-Za-z0-9_.]*)|(\$[A-Za-z_][A-Za-z0-9_.]*)\s(?=[\u4e00-\u9fff])", g):
    if in_macro(g, m.start()):
        continue
    n1 += 1
    if n1 <= 20:
        print(f"  @{m.start()}: {g[max(0,m.start()-70):m.start()+90]!r}")
print(f"  共 {n1} 处")

print("\n" + "=" * 95)
print("2. 内部名变量出现在正文（_output/_result/_temp/_args）")
print("=" * 95)
n2 = 0
for m in re.finditer(r"(?<![A-Za-z0-9_$])_(output|result|temp|args|tmp)\b", g):
    if in_macro(g, m.start()):
        continue
    pre = g[max(0, m.start() - 100):m.start()]
    if pre.rfind("<") > pre.rfind(">"):
        continue
    if pre and pre[-1] in ".=({[,;:+*/<>!&|?~^%$-":
        continue
    # 前后有中文
    ctx = g[max(0, m.start() - 60):m.start() + 100]
    if not re.search(r"[\u4e00-\u9fff]", ctx):
        continue
    n2 += 1
    if n2 <= 20:
        print(f"  @{m.start()}: {ctx!r}")
print(f"  共 {n2} 处")

print("\n" + "=" * 95)
print("3. undefined / NaN 在正文")
print("=" * 95)
n3 = 0
for m in re.finditer(r"\b(undefined|NaN)\b", g):
    if in_macro(g, m.start()):
        continue
    pre = g[max(0, m.start() - 120):m.start()]
    if pre.rfind("<") > pre.rfind(">"):
        continue
    # JS 上下文
    if re.search(r"typeof|\?\?|===|!==|\)\s*;|\bvar\b|\bconst\b|\blet\b", pre[-60:]):
        continue
    ctx = g[max(0, m.start() - 80):m.start() + 100]
    if not re.search(r"[\u4e00-\u9fff]", ctx):
        continue
    n3 += 1
    if n3 <= 20:
        print(f"  @{m.start()}  [{m.group(0)}]")
        print(f"    {ctx!r}")
print(f"  共 {n3} 处")

print("\n" + "=" * 95)
print("4. 双重转义 &amp;lt;&amp;lt;")
print("=" * 95)
raw = open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace")
n4 = len(re.findall(r"&amp;(?:lt|gt);", raw))
print(f"  共 {n4} 处")
for m in list(re.finditer(r"&amp;lt;", raw))[:8]:
    print(f"    @{m.start()}: {raw[max(0,m.start()-80):m.start()+120]!r}")

print("\n" + "=" * 95)
print("汇总")
print("=" * 95)
print(f"  变量旁有空格:  {n1}")
print(f"  内部名泄漏:    {n2}")
print(f"  undefined/NaN: {n3}")
print(f"  双重转义:      {n4}")
