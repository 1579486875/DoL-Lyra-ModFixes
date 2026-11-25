# -*- coding: utf-8 -*-
"""正确的重打包：以「当前 out 的 APK」为底，只替换 assets/www/index.html。

⚠ CUR19_pack.py 的 SRC 指向早期的 backup_r6，会丢掉后续所有资源改动，不要再用它。
"""
import os
import sys
import zipfile

BASE = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
IDX = r"E:\TAML\_dol\work\index_modded6.html"
OUT = r"E:\TAML\_dol\work\build_fixed_unsigned.apk"

if not os.path.exists(BASE):
    sys.exit("❌ 底包不存在: " + BASE)
if not os.path.exists(IDX):
    sys.exit("❌ index 不存在: " + IDX)

zb = zipfile.ZipFile(BASE)
new_index = open(IDX, "rb").read()
print("底包: %s" % BASE)
print("  大小: %.2f MB" % (os.path.getsize(BASE) / 1024 / 1024))
print("  条目: %d" % len(zb.namelist()))
print("新 index: %d 字节" % len(new_index))

old_idx_size = zb.getinfo("assets/www/index.html").file_size
print("旧 index: %d 字节" % old_idx_size)

TARGET = "assets/www/index.html"
n = 0
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zo:
    for info in zb.infolist():
        if info.filename == TARGET:
            # index.html 用新内容；保持 storE? 原版是 deflate
            data = new_index
            n += 1
        elif info.filename == "resources.arsc":
            # resources.arsc 必须保持 STORED（不压缩）
            data = zb.read(info.filename)
            zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            zi.compress_type = zipfile.ZIP_STORED
            zi.external_attr = info.external_attr
            zo.writestr(zi, data)
            n += 1
            continue
        else:
            data = zb.read(info.filename)
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, data)
        n += 1

print("写入条目: %d" % n)
print("✅ 输出: %s (%.2f MB)" % (OUT, os.path.getsize(OUT) / 1024 / 1024))

# 校验
zz = zipfile.ZipFile(OUT)
print("\n=== 校验 ===")
print("条目: %d (底包 %d)" % (len(zz.namelist()), len(zb.namelist())))
print("index: %d 字节" % zz.getinfo(TARGET).file_size)
print("arsc compress:", zz.getinfo("resources.arsc").compress_type, "(0=STORED)")
# 抽查 BESC / 图包关键文件
for k in ("assets/www/img/body/breasts/breasts6.png",
          "assets/www/img/clothes/under-upper/corset/6.png",
          "assets/www/img/transformations/demon/horns/default.png"):
    ok = k in zz.namelist()
    print("  %-58s %s" % (k.split("/")[-2] + "/" + k.split("/")[-1], "✅" if ok else "❌"))
