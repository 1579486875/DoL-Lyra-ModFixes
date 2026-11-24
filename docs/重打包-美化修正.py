# -*- coding: utf-8 -*-
"""把本地模组目录（美化修正）重新打包进 index。"""
import base64
import io
import json
import os
import re
import shutil
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
SRC = r"E:\TAML\_dol\work\_mods\44_美化修正"
MODE_NAME = "美化修正"
DRY = "--write" not in sys.argv


def build_zip(src_dir):
    """把目录打成 ZIP（保留相对路径，用正斜杠）。"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
        for root, dirs, files in os.walk(src_dir):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, src_dir).replace("\\", "/")
                zo.write(full, rel)
    return buf.getvalue()


def find_bj(raw):
    m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
    for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1)):
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
        if (bj.get("name") or "") == MODE_NAME:
            return s, zz, bj, m
    return None


raw = open(HTML, "rb").read().decode("utf-8", "replace")
found = find_bj(raw)
if not found:
    print("❌ 未找到", MODE_NAME)
    sys.exit(1)
s_old, zz, bj, m = found

new_zip = build_zip(SRC)
print("新 ZIP:", len(new_zip), "字节")
print("旧 ZIP 内文件:", zz.namelist())

# 校验新 ZIP 有效
try:
    zz2 = zipfile.ZipFile(io.BytesIO(new_zip))
    bj2 = json.loads(zz2.read("boot.json").decode("utf-8-sig"))
    print("新 ZIP 校验: ✅ name=%s 文件数=%d" % (bj2.get("name"), len(zz2.namelist())))
except Exception as e:
    print("❌ 新 ZIP 无效:", e)
    sys.exit(1)

new_b64 = base64.b64encode(new_zip).decode("ascii")
print("base64: %d -> %d" % (len(s_old), len(new_b64)))

if DRY:
    print("[dry-run] 加 --write 写入")
    sys.exit(0)

shutil.copy2(HTML, HTML + ".bak_before_beautylic")
raw2 = raw.replace(s_old, new_b64, 1)

n_before = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', m.group(1)))
m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw2, re.S)
n_after = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', m2.group(1)))
print("数组条目:", n_before, "->", n_after)
if n_before != n_after:
    sys.exit(1)

open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
