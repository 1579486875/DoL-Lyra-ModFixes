"""第 39 轮：找「数据值被翻译」导致的判断失效。

高风险模式：
  <<if $var is "中文">>        ← 如果 $var 实际存英文，永远不匹配
  <<if $var isnot "中文">>
  <<case "中文">>              ← 如果 switch 的值是英文，永远不命中
  .includes("中文")
  === "中文"
"""
import html
import re
import sys
import zipfile
from collections import Counter

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"
CJK = re.compile(r"[\u4e00-\u9fff]")


def load(p):
    z = zipfile.ZipFile(p)
    return html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


def scan(g, label):
    print("=" * 90)
    print(f"{label}")
    print("=" * 90)

    results = {}

    # 1) <<if $var is "中文">>
    pat1 = re.compile(r'<<if\s+\$[\w.]+\s+(is|isnot)\s+"([^"]*[\u4e00-\u9fff][^"]*)"')
    h1 = [(m.group(1), m.group(2), m.start()) for m in pat1.finditer(g)]
    print(f"  <<if $var is/isnot \"中文\">>: {len(h1)}")
    for op, v, pos in h1[:8]:
        print(f"    {op} {v!r}  @{pos}")
        print(f"      {g[max(0,pos-120):pos+120]!r}")
    results["if_cn"] = h1

    # 2) <<case "中文">>
    pat2 = re.compile(r'<<case\s+"([^"]*[\u4e00-\u9fff][^"]*)"')
    h2 = [(m.group(1), m.start()) for m in pat2.finditer(g)]
    print(f"\n  <<case \"中文\">>: {len(h2)}")
    for v, pos in h2[:8]:
        print(f"    {v!r}  @{pos}")
        print(f"      {g[max(0,pos-120):pos+120]!r}")
    results["case_cn"] = h2

    # 3) === "中文" / !== "中文"
    pat3 = re.compile(r'[!=]==?\s*"([^"]*[\u4e00-\u9fff][^"]*)"')
    h3 = [(m.group(1), m.start()) for m in pat3.finditer(g)]
    print(f"\n  === \"中文\": {len(h3)}")
    for v, pos in h3[:8]:
        print(f"    {v!r}  @{pos}")
        print(f"      {g[max(0,pos-100):pos+100]!r}")
    results["eq_cn"] = h3

    # 4) .includes("中文")
    pat4 = re.compile(r'\.includes\(\s*"([^"]*[\u4e00-\u9fff][^"]*)"\s*\)')
    h4 = [(m.group(1), m.start()) for m in pat4.finditer(g)]
    print(f"\n  .includes(\"中文\"): {len(h4)}")
    for v, pos in h4[:8]:
        print(f"    {v!r}  @{pos}")
        print(f"      {g[max(0,pos-100):pos+100]!r}")
    results["includes_cn"] = h4

    return results


mr = scan(load(APK), "modded")
vr = scan(load(VAN), "vanilla")

print("\n" + "=" * 90)
print("结论")
print("=" * 90)
total = 0
for k in mr:
    m_set = set(x[0] for x in mr[k])
    v_set = set(x[0] for x in vr[k])
    only = m_set - v_set
    print(f"  {k}: modded {len(mr[k])} / vanilla {len(vr[k])} → modded 独有 {len(only)}")
    if only:
        for x in list(only)[:8]:
            print(f"    ⚠️ {x!r}")
        total += len(only)

print()
if total:
    print(f"  ⚠️ modded 独有 {total} 处，需逐个人工确认")
else:
    print("  ✅ 无 modded 独有的「数据值被翻译」问题")

sys.exit(1 if total else 0)
