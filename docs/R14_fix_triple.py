"""第 14 轮：修 <<</if>> 三重尖括号 + 修审计脚本的闭合拼接 bug。

真 bug: <<</if>>  (3 个 <)  应为 <</if>>  (2 个 <)
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"

data = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(data)

print("=" * 80)
print("1) 当前 <<< 出现位置")
print("=" * 80)
triples = [(m.start(), g[max(0, m.start() - 150):m.start() + 150]) for m in re.finditer(r"<<<", g)]
print(f"  共 {len(triples)} 处")
for pos, ctx in triples:
    print(f"\n  @{pos}")
    print(f"    {ctx!r}")

print("\n" + "=" * 80)
print("2) vanilla 对照")
print("=" * 80)
import zipfile
vz = zipfile.ZipFile(VAN)
vg = H.unescape(vz.read("assets/www/index.html").decode("utf-8", "replace"))
vtri = [m.start() for m in re.finditer(r"<<<", vg)]
print(f"  vanilla {len(vtri)} 处")
for pos in vtri:
    print(f"    @{pos}: {vg[max(0,pos-80):pos+80]!r}")

print("\n" + "=" * 80)
print("3) 修复")
print("=" * 80)

# 只修 <<</xxx>> 这种（真 bug），不碰 <<< \n（SugarCube 的 blockquote 语法）
PAT = re.compile(r"<<<(/[a-z]+>>)")
hits = PAT.findall(g)
print(f"  找到 {len(hits)} 处 <<</xxx>>: {hits}")

total = 0
if hits:
    fixed_g = PAT.sub(r"<</\1", g)
    total = len(hits)
    data = H.escape(fixed_g, quote=False)
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"  ✅ 已修 {total} 处")

# 校验
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n=== 校验 ===")
rem = re.findall(r"<<<(/[a-z]+>>)", g2)
print(f"  <<</xxx>> 残留: {len(rem)}")
print(f"  <<< 总数: {g2.count('<<<')}  （vanilla 是 {len(vtri)}，其中 3 处是 WASM/blockquote 语法）")

# 修审计脚本
R12 = r"E:\TAML\_dol\work\R12_macro_pairs.py"
s = open(R12, encoding="utf-8").read()
OLD = 'closes = g.count("<<" + cl)'
NEW = 'closes = g.count("<" + cl + ">")   # 正确：cl 已含 < ，如 "</if>" -> "<</if>>"'
if OLD in s:
    s = s.replace(OLD, NEW)
    open(R12, "w", encoding="utf-8").write(s)
    print("\n  ✅ 已修正 R12 的闭合拼接 bug")
else:
    print("\n  （R12 无需修）")

sys.exit(0 if not rem else 1)
