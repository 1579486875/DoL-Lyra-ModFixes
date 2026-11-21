# -*- coding: utf-8 -*-
"""CUR19: 用修好的 index 重新打包（以 r6 包为底，保留全部资源），输出未签名 APK。"""
import os
import sys
import zipfile

SRC = r"E:\TAML\_dol\out\backups\DoL-Lyra-0.5.12.13-CHS-modded.apk.backup_r6_190337"
NEWHTML = r"E:\TAML\_dol\work\index_modded6.html"
DST = r"E:\TAML\_dol\work\build_fixed_unsigned.apk"

DROP = {"META-INF/DOL.SF", "META-INF/DOL.RSA", "META-INF/MANIFEST.MF"}
html = open(NEWHTML, "rb").read()
print("new index bytes:", len(html))

n = 0
with zipfile.ZipFile(SRC) as zin, zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zout:
    for info in zin.infolist():
        if info.filename in DROP:
            continue
        if info.filename.upper().startswith("META-INF/") and info.filename.upper().endswith((".SF", ".RSA", ".DSA")):
            continue
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.external_attr = info.external_attr
        if info.filename == "assets/www/index.html":
            zi.compress_type = zipfile.ZIP_DEFLATED
            zout.writestr(zi, html)
        elif info.filename == "resources.arsc":
            zi.compress_type = zipfile.ZIP_STORED
            zout.writestr(zi, zin.read(info.filename))
        else:
            zi.compress_type = info.compress_type
            zout.writestr(zi, zin.read(info.filename))
        n += 1

print("entries:", n, "size MB:", round(os.path.getsize(DST) / 1048576, 2))
with zipfile.ZipFile(DST) as z:
    print("testzip:", z.testzip())
    print("arsc compress:", z.getinfo("resources.arsc").compress_type)
    print("index bytes:", z.getinfo("assets/www/index.html").file_size)
    print("has META-INF sig:", [x for x in z.namelist() if x.upper().endswith(('.SF', '.RSA', '.DSA'))][:3])
