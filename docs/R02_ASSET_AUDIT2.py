# -*- coding: utf-8 -*-
"""第2轮b：只看真正的图片文件缺失（以 .png/.jpg/.gif 结尾）。"""
import re
import zipfile
from collections import Counter

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
names = set(z.namelist())
assets = {n[len("assets/www/"):] for n in names if n.startswith("assets/www/")}

idx = z.read("assets/www/index.html").decode("utf-8", "replace")

# 只取以图片扩展名结尾的引用
refs = set()
for m in re.finditer(r'["\']((?:img|audio|fonts)/[^"\']{2,140}\.(?:png|jpg|jpeg|gif|webp|ogg|mp3|woff2?|ttf))["\']', idx, re.I):
    refs.add(m.group(1))

print("图片/音频引用:", len(refs))
missing = sorted(r for r in refs if r not in assets)
print("缺失:", len(missing))
for r in missing:
    # 找引用上下文
    i = idx.find('"' + r + '"')
    if i < 0:
        i = idx.find(r)
    ctx = idx[max(0, i - 90):i + 40].replace("\n", " ")
    print("  %-52s | %s" % (r, ctx[-110:]))
