"""第 15-20 轮：比较值 / case 标签是否被 i18n 翻译（会导致分支永不命中）。

危险模式：
  <<if $speech_attitude is "meek">>  →  <<if $speech_attitude is "温顺">>  ← 永不匹配
  <<case Bailey>>                   →  <<case 贝利>>                    ← 永不匹配
"""
import html
import re
from collections import Counter

HTML = r"E:\TAML\_dol\work\index_modded6.html"
g = html.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))

CJK = re.compile(r"[\u4e00-\u9fff]")

print("=" * 94)
print("第 15 轮：<<if $var is \"中文\">> —— 比较值被翻译")
print("=" * 94)
bad = []
for m in re.finditer(r'<<(?:if|elseif)\s+\$[\w.\[\]]+\s+is(?:not)?\s+"([^"]{1,40})"', g):
    if CJK.search(m.group(1)):
        bad.append((m.group(1), g[max(0, m.start() - 60):m.start() + 120]))
print(f"  命中 {len(bad)} 处")
for v, ctx in bad[:15]:
    print(f"    值={v!r}")
    print(f"      {ctx!r}")

print("\n" + "=" * 94)
print("第 16 轮：<<case 中文字>> —— switch 分支被翻译")
print("=" * 94)
cases = Counter()
for m in re.finditer(r"<<case\s+([^>\s][^>]{0,40}?)>>", g):
    v = m.group(1).strip()
    cases[v] += 1
cjk_cases = {k: v for k, v in cases.items() if CJK.search(k)}
print(f"  <<case>> 共 {len(cases)} 种，其中含中文的 {len(cjk_cases)} 种")
for k, v in Counter(cjk_cases).most_common(20):
    print(f"    {v:>3}  {k!r}")

print("\n" + "=" * 94)
print("第 17 轮：<<set $var to \"中文\">> —— 赋值被翻译（可能是枚举值）")
print("=" * 94)
# 只挑「看起来像枚举」的短中文值
assigns = Counter()
for m in re.finditer(r'<<set\s+\$[\w.\[\]]+\s+to\s+"([^"]{1,20})"', g):
    v = m.group(1)
    if CJK.search(v) and len(v) <= 8:
        assigns[v] += 1
print(f"  短中文赋值值: {len(assigns)} 种")
for k, v in assigns.most_common(20):
    print(f"    {v:>3}  {k!r}")

print("\n" + "=" * 94)
print("第 18 轮：<<link [[中文|英文Passage]]>> 的目标是否存在")
print("=" * 94)
passages = set(html.unescape(x) for x in re.findall(r'<tw-passagedata[^>]*name="([^"]+)"', 
              open(HTML, "rb").read().decode("utf-8", "replace")))
links = re.findall(r"\[\[([^\]|]+)\|([^\]]+)\]\]", g)
missing = Counter()
for label, target in links:
    t = target.strip()
    if t.startswith("$") or t.startswith("_") or "<<" in t:
        continue
    if t not in passages:
        missing[t] += 1
print(f"  链接 {len(links)} 条，目标不存在的 {len(missing)} 种")
for k, v in missing.most_common(15):
    print(f"    {v:>3}  {k!r}")

print("\n" + "=" * 94)
print("第 19 轮：存档变量是否被翻译成中文名")
print("=" * 94)
vars_cn = set()
for m in re.finditer(r"\$([\u4e00-\u9fff][\w]*)", g):
    vars_cn.add(m.group(1))
print(f"  中文变量名: {len(vars_cn)} 个")
for v in list(vars_cn)[:10]:
    print(f"    ${v}")

print("\n" + "=" * 94)
print("第 20 轮：<<widget>> 名与调用是否一一对应")
print("=" * 94)
defs = set(re.findall(r'<<widget\s+"([^"]+)"', g))
calls = Counter(re.findall(r"<<([a-zA-Z][\w\-]*)", g))
# 只统计有定义的
missing_calls = []
for name, c in calls.items():
    if name in defs:
        continue
# 反向：定义了但从未调用
unused = [d for d in defs if calls.get(d, 0) == 0]
print(f"  widget 定义 {len(defs)} 个，从未被调用 {len(unused)} 个")
for u in unused[:10]:
    print(f"    {u}")
