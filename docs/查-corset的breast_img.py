# -*- coding: utf-8 -*-
"""精确提取 corset 的 breast_img 映射表。"""
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")

# 定位 corset 的 ClothesItem（以 variable: "corset" 为锚）
i = h.find('variable: "corset"')
if i < 0:
    raise SystemExit("❌ 未找到 corset 定义")

# 向后 3000 字符内找 breast_img
seg = h[i:i + 3000]
m = re.search(r"breast_img\s*:\s*(\{[^}]*\}|\d+)", seg)
if m:
    print("corset 的 breast_img =", m.group(1))
else:
    print("❌ 未找到 breast_img，打印附近内容：")
    print(seg[:1500])

# 同时看 bustresize
m2 = re.search(r"bustresize\s*:\s*(\d+)", seg)
print("corset 的 bustresize =", m2.group(1) if m2 else "?")

# 对照几个同槽位的
print("\n=== 其他 under_upper 的 breast_img 作对比 ===")
for nm in ("mesh shirt", "corset", "fishnet top", "binder"):
    j = h.find('variable: "%s"' % nm.replace(" ", ""))
    if j < 0:
        j = h.find('name: "%s"' % nm)
    if j < 0:
        continue
    s2 = h[j:j + 2500]
    m3 = re.search(r"breast_img\s*:\s*(\{[^}]*\}|\d+)", s2)
    m4 = re.search(r"bustresize\s*:\s*(\d+)", s2)
    print("  %-14s breast_img=%-52s bustresize=%s" % (
        nm, m3.group(1) if m3 else "?", m4.group(1) if m4 else "?"))
