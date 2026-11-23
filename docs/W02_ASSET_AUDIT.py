# -*- coding: utf-8 -*-
"""第2轮：全量资源审计 —— index 引用 vs APK 内实有文件（含模组 ZIP 内资源）。"""
import base64
import io
import json
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
names = set(z.namelist())
assets = {n[len("assets/www/"):] for n in names if n.startswith("assets/www/")}
idx = z.read("assets/www/index.html").decode("utf-8", "replace")

# 收集模组 ZIP 内的资源
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", idx, re.S)
mod_assets = set()
if m:
    for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1)):
        try:
            d = base64.b64decode(re.sub(r"\s+", "", s))
        except Exception:
            continue
        if d[:2] != b"PK":
            continue
        try:
            zz = zipfile.ZipFile(io.BytesIO(d))
            for n in zz.namelist():
                if re.search(r"\.(png|jpg|jpeg|gif|webp|ogg|mp3|woff2?|ttf|svg)$", n, re.I):
                    mod_assets.add(n)
        except Exception:
            continue
print("APK assets:", len(assets), "| 模组资源:", len(mod_assets))

# index 引用的图片/音频
refs = set()
for mm in re.finditer(r'["\']((?:img|audio|fonts)/[^"\']{2,140}\.(?:png|jpg|jpeg|gif|webp|ogg|mp3|woff2?|ttf))["\']', idx, re.I):
    refs.add(mm.group(1))
print("index 引用:", len(refs))

missing = sorted(r for r in refs if r not in assets and r not in mod_assets)
print("\nAPK 和模组里都没有的:", len(missing))
# 排除原版已知缺失（img/sex/*/active/ 图层）
real = [r for r in missing if "/active/" not in r and not r.startswith("img/clothers/")]
print("排除已知缺失后:", len(real))
for r in real[:30]:
    print("  ", r)
