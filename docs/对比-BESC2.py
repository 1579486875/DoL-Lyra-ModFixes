# -*- coding: utf-8 -*-
"""对比 BESC 最新版与我们包里的 img/（修正路径前缀）。"""
import hashlib
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
BESC = r"E:\TAML\_dol\work\besc.zip"

z_apk = zipfile.ZipFile(APK)
z_besc = zipfile.ZipFile(BESC)

# BESC: .../img/body/xxx.png -> body/xxx.png
besc_files = {}
for n in z_besc.namelist():
    if n.endswith("/") or not n.endswith(".png"):
        continue
    parts = n.split("/", 1)
    if len(parts) < 2:
        continue
    rel = parts[1]
    if rel.startswith("img/"):
        rel = rel[4:]
    data = z_besc.read(n)
    besc_files[rel] = (len(data), hashlib.md5(data).hexdigest())

# 我们: assets/www/img/body/xxx.png -> body/xxx.png
apk_files = {}
for n in z_apk.namelist():
    if not n.startswith("assets/www/img/") or not n.endswith(".png"):
        continue
    rel = n[len("assets/www/img/"):]
    apk_files[rel] = z_apk.getinfo(n).file_size

print("BESC PNG:", len(besc_files))
print("我们 PNG:", len(apk_files))

missing = []
diff = []
same = 0
for rel, (sz, md5) in besc_files.items():
    if rel not in apk_files:
        missing.append((rel, sz))
    elif apk_files[rel] != sz:
        diff.append((rel, sz, apk_files[rel]))
    else:
        same += 1

print("\n=== 结果 ===")
print("BESC 有我们没有:", len(missing))
print("大小不同:", len(diff))
print("相同:", same)

if missing:
    print("\n=== 缺失（前 40）===")
    for rel, sz in sorted(missing)[:40]:
        print("   %-56s %6d" % (rel, sz))

if diff:
    print("\n=== 大小不同（前 25）===")
    for rel, a, b in sorted(diff)[:25]:
        print("   %-50s BESC=%6d 我们=%6d  差=%+d" % (rel, a, b, a - b))
