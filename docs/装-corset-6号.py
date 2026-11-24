# -*- coding: utf-8 -*-
"""装 C_激进 版为 corset/6.png，并把 breast_img 的 4/5/6 都指向 6。

映射设计（配合 bustresize: +2）：
  真实 0/1 (+2→2/3) -> 1.png
  真实 2   (+2→4)   -> 2.png
  真实 3   (+2→5)   -> 3.png
  真实 4   (+2→6)   -> 6.png   ← 用户的场景
  真实 5/6          -> 6.png
"""
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
NEW6 = r"E:\TAML\_dol\work\诊断-三类服装\corset-6号\C_激进.png"
OUT = r"E:\TAML\_dol\work\DoL-corset-v3.apk"

z = zipfile.ZipFile(APK)
h = z.read("assets/www/index.html").decode("utf-8", "replace")

# 定位 corset 的 breast_img
i = h.find('variable: "corset"')
if i < 0:
    raise SystemExit("❌ 未找到 corset")
seg = h[i:i + 3000]
m = re.search(r"breast_img\s*:\s*\{[^}]*\}", seg)
if not m:
    raise SystemExit("❌ 未找到 breast_img")

old_bi = m.group(0)
print("原:", old_bi)

NEW_BI = "breast_img: { 0: 1, 1: 1, 2: 2, 3: 3, 4: 6, 5: 6, 6: 6 }"
h2 = h[:i + m.start()] + NEW_BI + h[i + m.end():]
print("新:", NEW_BI)
assert h2.count(NEW_BI) == 1, "替换异常"
print("✅ 映射已改")

# 6.png
data6 = open(NEW6, "rb").read()
print("新 6.png:", len(data6), "字节")

DST6 = "assets/www/img/clothes/under-upper/corset/6.png";

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in z.infolist():
        if info.filename == "assets/www/index.html":
            d = h2.encode("utf-8")
        elif info.filename == DST6:
            d = data6
        else:
            d = z.read(info.filename)
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, d)

print("\n✅ 输出:", OUT)

z2 = zipfile.ZipFile(OUT)
print("   条目:", len(z2.namelist()), "(原", len(z.namelist()), ")")
print("   6.png:", z2.getinfo(DST6).file_size)
h3 = z2.read("assets/www/index.html").decode("utf-8", "replace")
print("   新映射存在:", NEW_BI in h3)
print("   旧映射已消:", old_bi not in h3)
