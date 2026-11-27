# -*- coding: utf-8 -*-
"""验证 MapleBirchCE 的拖动修复是否还在（当前包 vs work 源）。"""
import base64
import io
import json
import re
import zipfile

def check(label, get_html):
    h = get_html()
    mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", h, re.S)
    if not mz:
        print("[%s] 找不到 modDataValueZipList" % label)
        return
    for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', mz.group(1)):
        try:
            d = base64.b64decode(re.sub(r"\s+", "", s))
        except Exception:
            continue
        if d[:2] != b"PK":
            continue
        try:
            zz = zipfile.ZipFile(io.BytesIO(d))
            bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
        except Exception:
            continue
        if (bj.get("name") or "") != "MapleBirchCE":
            continue
        js = zz.read("javascript/maplebirchce.js").decode("utf-8", "replace")
        print("\n[%s] MapleBirchCE" % label)
        print("  maplebirchce.js: %d 字节" % len(js))
        print("  _mbceZoomScale          :", "✅" if "_mbceZoomScale" in js else "❌")
        print("  _zsv (钳位)             :", js.count("_zsv"), "处")
        print("  残留裸 innerWidth 钳位   :", len(re.findall(r'window\.innerWidth\) \|\| 1280;', js)))
        print("  残留 drag.l = r.left    :", len(re.findall(r"drag\.l = r\.left;", js)))
        print("  _sl (style 坐标)        :", js.count("_sl"), "处")
        return
    print("[%s] 没找到 MapleBirchCE" % label)


# 1) 当前 out 包
def from_apk():
    z = zipfile.ZipFile(r"E:\TAML\_dol\out\育都孤儿-GNH个人整合版-2026.11.26.apk")
    return z.read("assets/www/index.html").decode("utf-8", "replace")

# 2) work 源
def from_work():
    return open(r"E:\TAML\_dol\work\index_modded6.html", encoding="utf-8").read()

check("out 包", from_apk)
check("work\\index_modded6.html", from_work)
