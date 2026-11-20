"""AC02：判断这 2832 条英文描述是否真的会显示给玩家。

关键：如果 JS 对象里有 desc_CN / name_CN 之类的对应字段，说明已翻译。
     否则运行时就是英文。
"""
import html as H
import re
import json

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

print("=" * 95)
print("1. 有没有 _CN 后缀的对应字段")
print("=" * 95)
for suf in ("_CN", "_cn", "Cn", "ChineseCN", "_cn_name", "cn_name"):
    # 形如 desc_CN: / name_CN:
    n = len(re.findall(r"\b(?:desc|name|description|title|text|label)" + re.escape(suf) + r"\s*:", g))
    print(f"  {suf:<12} 形如 xxx{suf}: 的字段  {n} 处")

print("\n" + "=" * 95)
print("2. 具体的例子：A basic sleep gown.")
print("=" * 95)
for m in list(re.finditer(r"A basic sleep gown\.", g))[:3]:
    print(f"  @{m.start()}: {g[max(0, m.start() - 250):m.start() + 300]!r}")
    print()

print("=" * 95)
print("3. 成就名 A Crime Most Foul")
print("=" * 95)
for m in list(re.finditer(r"A Crime Most Foul", g))[:3]:
    print(f"  @{m.start()}: {g[max(0, m.start() - 250):m.start() + 300]!r}")
    print()

print("=" * 95)
print("4. 服装描述 A classic plaid skirt.")
print("=" * 95)
for m in list(re.finditer(r"A classic plaid skirt\.", g))[:2]:
    print(f"  @{m.start()}: {g[max(0, m.start() - 250):m.start() + 300]!r}")
    print()
