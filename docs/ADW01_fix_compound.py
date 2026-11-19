"""修 $compoundWraith 被误改成 $compound 的问题。

vanilla: <<if $compoundWraith>><<set $compound.wraith to $compoundWraith>><</if>>
错误版: <<if $compound>><<set $compound.wraith to $compound>><</if>>
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

data = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(data)

print("=" * 80)
print("当前状态")
print("=" * 80)
for m in re.finditer(r"<<if \$compound>>.*?<</if>>", g, re.S):
    print(f"  {m.group(0)[:200]!r}")

# 精确替换
FIXES = [
    ("<<if $compound>>\n\t\t\t<<set $compound.wraith to $compound>>\n\t\t<</if>>",
     "<<if $compoundWraith>>\n\t\t\t<<set $compound.wraith to $compoundWraith>>\n\t\t<</if>>"),
    ("<<if $compound>><<set $compound.wraith to $compound>><</if>>",
     "<<if $compoundWraith>><<set $compound.wraith to $compoundWraith>><</if>>"),
]

total = 0
for old, new in FIXES:
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            n = data.count(a)
            data = data.replace(a, b)
            total += n
            print(f"\n✅ 修复 {n} 处")
            print(f"    {old[:80]!r}")
            break
    if total:
        break

if total:
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}")
else:
    print("\n（未命中，用正则）")
    pat = re.compile(r"<<if \$compound>>\s*<<set \$compound\.wraith to \$compound>>\s*<</if>>")
    if pat.search(g):
        new_g = pat.sub("<<if $compoundWraith>><<set $compound.wraith to $compoundWraith>><</if>>", g)
        data = H.escape(new_g, quote=False)
        open(HTML, "wb").write(data.encode("utf-8"))
        print("✅ 正则修复成功")
        total = 1

# 校验
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n=== 校验 ===")
print(f"  $compoundWraith: {len(re.findall('[$]compoundWraith', g2))} 处")
print(f"  错误的 <<if $compound>>: {len(re.findall(chr(60)*2 + 'if [$]compound' + chr(62)*2, g2))} 处")
