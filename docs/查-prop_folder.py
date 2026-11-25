# -*- coding: utf-8 -*-
"""查 T.modeloptions.prop 的 folder 是怎么来的。"""
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")

print("=== modeloptions.prop 赋值 ===")
for mm in list(re.finditer(r"modeloptions\.prop\s*=", h))[:5]:
    print("\n@%d:" % mm.start())
    print(h[max(0, mm.start() - 200):mm.start() + 1200].replace("\n", " ")[:1400])
    print()

print("\n=== .folder 的所有赋值 ===")
for mm in list(re.finditer(r"\.folder\s*[:=]", h))[:10]:
    print("\n@%d: %s" % (mm.start(), h[max(0, mm.start() - 300):mm.start() + 300].replace("\n", " ")[:560]))

print("\n\n=== wearProp 宏的完整定义 ===")
for m in re.finditer(r"Macro\.add\(\s*[\"']wearProp[\"']", h):
    print("\n@%d:" % m.start())
    print(h[m.start():m.start() + 2500])
    break
else:
    # 找 widget
    m2 = re.search(r'<<"wearProp">>|widget "wearProp"', h)
    if m2:
        print(h[max(0, m2.start() - 100):m2.start() + 2000])
