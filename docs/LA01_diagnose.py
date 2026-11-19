"""紧急诊断：查 relation-box 的 if 语法错误 / NPC_CN_* 宏 / faceVariantOptions。"""
import html
import re

HTML = r"E:\TAML\_dol\work\index_modded6.html"
g = html.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))

print("=" * 94)
print("1) relation-box widget 全文")
print("=" * 94)
m = re.search(r'<<widget\s+"relation-box"\s*>>(.*?)<</widget>>', g, re.S)
if m:
    body = m.group(1)
    print(f"长度 {len(body)}")
    print(body[:3000])
else:
    print("未找到")

print("\n" + "=" * 94)
print("2) NPC_CN_NAME / NPC_CN_TYPE 宏是否被定义")
print("=" * 94)
for kw in ("NPC_CN_NAME", "NPC_CN_TYPE", "BODYPARTS_CN_NAME", "NPC_CN_TOOLNAME"):
    defs = re.findall(r'<<widget\s+"' + kw + r'"', g)
    calls = len(re.findall(r"<<" + kw + r"\b", g))
    print(f"  {kw:<22} 宏定义 {len(defs)}  调用 {calls}")

print("\n" + "=" * 94)
print("3) setup.NPC_CN_* 函数是否被定义（静态）")
print("=" * 94)
for kw in ("NPC_CN_NAME", "NPC_CN_TYPE", "NPC_CN_TITLE", "BODYPARTS_CN_NAME"):
    d = len(re.findall(r"setup\." + kw + r"\s*=", g))
    c = len(re.findall(r"setup\." + kw + r"\(", g))
    print(f"  setup.{kw:<22} 定义 {d}  调用 {c}")

print("\n" + "=" * 94)
print("4) faceVariantOptions 现状")
print("=" * 94)
m = re.search(r"<<set setup\.faceVariantOptions to \{(.*?)\}\s*>>", g, re.S)
if m:
    keys = re.findall(r'"([^"]+)"\s*:', m.group(1))
    print(f"  键数 {len(keys)}: {keys}")
else:
    print("  未找到")

print("\n" + "=" * 94)
print("5) cheatsDemeanour 现状")
print("=" * 94)
m = re.search(r'<<widget\s+"cheatsDemeanour"\s*>>(.*?)<</widget>>', g, re.S)
if m:
    print(m.group(1)[:800])

print("\n" + "=" * 94)
print("6) relation-box 里所有 <<if>> 的内容")
print("=" * 94)
if m:
    pass
# 重新找 relation-box（上面 m 被覆盖了）
m2 = re.search(r'<<widget\s+"relation-box"\s*>>(.*?)<</widget>>', g, re.S)
if m2:
    for mm in re.finditer(r"<<if\b[^>]{0,300}>>", m2.group(1)):
        txt = mm.group(0)
        if "<<" in txt[4:]:
            print(f"  ⚠️ 含 << {txt[:250]!r}")
