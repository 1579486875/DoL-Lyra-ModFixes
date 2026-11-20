"""V02：扫 <<case>> / <<switch>> / <<set>> 匹配值被翻译的情况。

这类是「数据被当文本翻了」，会导致分支永远匹配不上 → 功能静默失效。
"""
import html as H
import json
import re
from collections import Counter

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))
gb = H.unescape(__import__("zipfile").ZipFile(
    r"E:\TAML\_dol\archive\DoL-Lyra-0.5.12.13-CHS-modded_20261120-061313_修复arsc可安装.apk"
).read("assets/www/index.html").decode("utf-8", "replace"))

print("=" * 95)
print("1. <<case>> 值含中文（数据被翻译）")
print("=" * 95)
n = 0
for m in re.finditer(r"<<case\s+([^>]{0,300})>>", g):
    vals = m.group(1)
    if re.search(r"[\u4e00-\u9fff]", vals):
        n += 1
        if n <= 25:
            print(f"  @{m.start()}")
            print(f"    {m.group(0)[:220]!r}")
print(f"  共 {n} 处")

print("\n" + "=" * 95)
print("2. 基线里同样位置的情况（对比）")
print("=" * 95)
nb = 0
for m in re.finditer(r"<<case\s+([^>]{0,300})>>", gb):
    if re.search(r"[\u4e00-\u9fff]", m.group(1)):
        nb += 1
print(f"  基线: {nb} 处 / 当前: {n} 处")

print("\n" + "=" * 95)
print("3. <<switch>> 表达式含中文")
print("=" * 95)
n3 = 0
for m in re.finditer(r"<<switch\s+([^>]{0,200})>>", g):
    if re.search(r"[\u4e00-\u9fff]", m.group(1)):
        n3 += 1
        if n3 <= 10:
            print(f"  {m.group(0)[:200]!r}")
print(f"  共 {n3} 处")

print("\n" + "=" * 95)
print("4. <<if>> 里两个字符串比较、其中一边是中文（可能是数据被翻）")
print("=" * 95)
n4 = 0
for m in re.finditer(r'<<if\b[^>]{0,300}?"([^"]*[\u4e00-\u9fff][^"]*)"[^>]{0,300}?>>', g):
    n4 += 1
    if n4 <= 20:
        print(f"  @{m.start()}: {m.group(0)[:220]!r}")
print(f"  共 {n4} 处")

print("\n" + "=" * 95)
print("5. set 赋中文字符串（可能破坏状态判断）")
print("=" * 95)
n5 = 0
for m in re.finditer(r'<<set\s+\$([A-Za-z_][A-Za-z0-9_.\[\]]*)\s+to\s+"([^"]*[\u4e00-\u9fff][^"]*)"', g):
    n5 += 1
    if n5 <= 20:
        print(f"  ${m.group(1)} = {m.group(2)[:60]!r}")
print(f"  共 {n5} 处")

print("\n" + "=" * 95)
print("汇总")
print("=" * 95)
print(f"  <<case>> 含中文:   {n}")
print(f"  <<switch>> 含中文: {n3}")
print(f"  <<if>> 含中文字符串: {n4}")
print(f"  <<set>> 赋中文字符串: {n5}")
