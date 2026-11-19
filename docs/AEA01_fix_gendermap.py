"""修性别化身体选择器的 JS 对象键被翻译问题。

错误: ({'男':'m','女':'f','中':'a'})[_bodyTypes[_i].charAt(0)]
       —— _bodyTypes[i].charAt(0) 返回 'm'/'f'/'a'，中文键永远查不到
正确: 直接用 _bodyTypes[_i].charAt(0) 比较
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
for m in re.finditer(r"\{'男':'m','女':'f','中':'a'\}", g):
    print(f"  {g[max(0,m.start()-180):m.start()+180]!r}")

print("\n" + "=" * 80)
print("vanilla 原文")
print("=" * 80)
import zipfile
vz = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk")
vg = H.unescape(vz.read("assets/www/index.html").decode("utf-8", "replace"))
for m in list(re.finditer(r"_bodyTypes\[_i\]\.charAt\(0\)", vg))[:3]:
    print(f"  {vg[max(0,m.start()-200):m.start()+200]!r}")

print("\n" + "=" * 80)
print("修复")
print("=" * 80)

# 1) 中文键对象 -> 恒等映射（保留结构但值正确）
FIX1 = [
    ("({'男':'m','女':'f','中':'a'})", "{m:'m',f:'f',a:'a'}"),
    ('({\'男\':\'m\',\'女\':\'f\',\'中\':\'a\'})', "{m:'m',f:'f',a:'a'}"),
]
total = 0
for old, new in FIX1:
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            n = data.count(a)
            data = data.replace(a, b)
            total += n
            print(f"  ✅ {old} -> {new}  ({n})")
            break
    if total:
        break

if not total:
    # 正则兜底
    pat = re.compile(r"\(\{[^}]*'男'[^}]*'女'[^}]*'中'[^}]*\}\)")
    if pat.search(g):
        new_g = pat.sub("{m:'m',f:'f',a:'a'}", g)
        data = H.escape(new_g, quote=False)
        total = 1
        print("  ✅ 正则替换成功")
    else:
        print("  ❌ 未找到")

if total:
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}")

# 校验
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n=== 校验 ===")
print(f"  中文键残留: {len(re.findall(chr(123) + chr(39) + '男', g2))}")
print(f"  新写法: {len(re.findall(chr(123) + 'm:' + chr(39) + 'm', g2))}")
