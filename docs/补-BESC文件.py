# -*- coding: utf-8 -*-
"""把 BESC 里我们缺失的文件补进 APK 的 assets/www/img/。"""
import hashlib
import os
import shutil
import sys
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
BESC = r"E:\TAML\_dol\work\besc.zip"
OUT = r"E:\TAML\_dol\work\DoL-BESC-filled.apk"
DRY = "--write" not in sys.argv

z_apk = zipfile.ZipFile(APK)
z_besc = zipfile.ZipFile(BESC)

# BESC 文件表（去 img/ 前缀）
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
    besc_files["assets/www/img/" + rel] = n

# 我们已有的
apk_names = set(z_apk.namelist())

missing = [(k, v) for k, v in besc_files.items() if k not in apk_names]
print("待补文件:", len(missing))

if not missing:
    print("无需补")
    sys.exit(0)

# 统计大小
total = sum(z_besc.getinfo(n).file_size for k, n in missing)
print("总大小: %.1f MB" % (total / 1024 / 1024))

if DRY:
    print("[dry-run] 加 --write 写入")
    # 显示前 20 个
    for k, n in sorted(missing)[:20]:
        print("   ", k)
    sys.exit(0)

# 重建 APK
print("\n重建 APK ...")
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zo:
    # 先复制原有文件
    cnt = 0
    for info in z_apk.infolist():
        data = z_apk.read(info.filename)
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, data)
        cnt += 1
        if cnt % 5000 == 0:
            print("   已复制 %d / %d" % (cnt, len(z_apk.infolist())))
    print("   原有文件复制完成:", cnt)

    # 补 BESC 缺失文件
    for k, n in missing:
        data = z_besc.read(n)
        zi = zipfile.ZipInfo(k, date_time=(2026, 1, 1, 0, 0, 0))
        zi.compress_type = zipfile.ZIP_DEFLATED
        zo.writestr(zi, data)
    print("   已补入:", len(missing))

print("\n✅ 输出:", OUT)
print("   大小: %.2f MB" % (os.path.getsize(OUT) / 1024 / 1024))
