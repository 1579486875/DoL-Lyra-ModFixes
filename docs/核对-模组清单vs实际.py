# -*- coding: utf-8 -*-
"""核对 Clothes 模组 boot.json 里声明的 imgFileList 与实际 ZIP 内容是否一致。

这能找出所有「声明了但缺失」的图 —— 它们会在运行时报 404。
"""
import base64
import io
import json
import re
import zipfile

APK = r"E:\TAML\_dol\out\育都孤儿-GNH个人整合版-2026.11.26.apk"
z = zipfile.ZipFile(APK)
h = z.read("assets/www/index.html").decode("utf-8", "replace")
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", h, re.S)

print("=== 全体模组：boot.json 声明的文件 vs ZIP 实际内容 ===")
total_missing = 0
report = []

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
    nm = bj.get("name") or "?"
    names = set(zz.namelist())
    missing = []
    for field in ("imgFileList", "scriptFileList", "tweeFileList", "styleFileList",
                  "scriptFileList_earlyload", "scriptFileList_inject_early",
                  "scriptFileList_preload", "additionFile"):
        for f in (bj.get(field) or []):
            if isinstance(f, str) and f not in names:
                missing.append((field, f))
    if missing:
        report.append((nm, len(missing), missing))
        total_missing += len(missing)

report.sort(key=lambda x: -x[1])
print("有缺失的模组: %d 个，共 %d 项\n" % (len(report), total_missing))
for nm, c, missing in report:
    print("\n【%s】%d 项" % (nm, c))
    by_field = {}
    for f_, f in missing:
        by_field.setdefault(f_, []).append(f)
    for f_, items in by_field.items():
        print("   %s: %d 项" % (f_, len(items)))
        for x in items[:5]:
            print("      %s" % x)
        if len(items) > 5:
            print("      ... 共 %d（前5）" % len(items))
