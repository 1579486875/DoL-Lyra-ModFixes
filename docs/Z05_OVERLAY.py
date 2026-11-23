# -*- coding: utf-8 -*-
"""第5轮：扫描所有「点外部关闭浮层」的实现，检查是否绑在冒泡阶段（易被 stopPropagation 拦）。"""
import base64
import html as H
import io
import json
import re
import zipfile

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

print("=== index：document.addEventListener('click') 无捕获 ===")
# 冒泡阶段（没有第三个参数 true）
for m in re.finditer(r'document\.addEventListener\(\s*["\'](click|touchend|mousedown)["\']\s*,\s*([A-Za-z_$][\w$]*)\s*\)', g):
    seg = g[max(0, m.start() - 300):m.start() + 200]
    # 只看和「关闭/移除」相关的
    if re.search(r"(remove|close|hide|dismiss|cleanup|removeChild|\.remove\(\))", seg, re.I):
        print("   @%d [%s] %s" % (m.start(), m.group(1), repr(seg)[:400]))
        print()

print("\n=== index：$(document).on('click') / body.on ===")
for m in re.finditer(r'\$\(\s*(document|"body"|\'body\'|document\.body)\s*\)\.(on|bind|click)\(\s*["\']?(click)?', g):
    seg = g[max(0, m.start() - 200):m.start() + 250]
    if re.search(r"(remove|close|hide|dismiss)", seg, re.I):
        print("   @%d %s" % (m.start(), repr(seg)[:380]))
        print()

print("\n=== 模组：同类模式 ===")
raw = open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace")
mm = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', mm.group(1))
for s in parts:
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
    nm = bj.get("name") or "?"
    for info in zz.infolist():
        if info.file_size > 3 * 1024 * 1024:
            continue
        try:
            t = zz.read(info).decode("utf-8", "replace")
        except Exception:
            continue
        for m2 in re.finditer(r'(?:document|\$\(document\)|window)\.addEventListener\(\s*["\'](click|touchend)["\']\s*,\s*([A-Za-z_$][\w$]*)\s*\)', t):
            seg = t[max(0, m2.start() - 250):m2.start() + 180]
            if re.search(r"(remove|close|hide|dismiss)", seg, re.I):
                print("  [%s] %s :: %s" % (nm, info.filename, repr(seg)[:380]))
