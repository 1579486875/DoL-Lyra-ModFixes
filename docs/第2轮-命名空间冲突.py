# -*- coding: utf-8 -*-
"""第2轮：审计所有模组往 window / setup / V / T 上挂的全局名，找重名冲突。"""
import base64
import io
import json
import re
import zipfile
from collections import defaultdict

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", h, re.S)

# 收集
win_names = defaultdict(set)     # name -> {mod}
setup_names = defaultdict(set)
t_names = defaultdict(set)
fn_names = defaultdict(set)      # function 声明

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
    for f in zz.namelist():
        if not f.lower().endswith(".js"):
            continue
        try:
            if zz.getinfo(f).file_size > 3_000_000:
                continue
            t = zz.read(f).decode("utf-8", "replace")
        except Exception:
            continue
        for mm in re.finditer(r"window\.([A-Za-z_$][\w$]*)\s*=", t):
            win_names[mm.group(1)].add(nm)
        for mm in re.finditer(r"\bsetup\.([A-Za-z_$][\w$]*)\s*=", t):
            setup_names[mm.group(1)].add(nm)
        for mm in re.finditer(r"\bT\.([A-Za-z_$][\w$]*)\s*=", t):
            t_names[mm.group(1)].add(nm)

print("=== window 上被多个模组赋值的名字 ===")
conf = {k: v for k, v in win_names.items() if len(v) >= 2}
if not conf:
    print("  ✅ 无冲突")
for k in sorted(conf):
    print("  ⚠️ window.%-32s %s" % (k, sorted(conf[k])))

print("\n=== setup 上被多个模组赋值的名字 ===")
conf2 = {k: v for k, v in setup_names.items() if len(v) >= 2}
if not conf2:
    print("  ✅ 无冲突")
for k in sorted(conf2):
    print("  ⚠️ setup.%-32s %s" % (k, sorted(conf2[k])))

print("\n=== T 上被多个模组赋值的名字 ===")
conf3 = {k: v for k, v in t_names.items() if len(v) >= 2}
if not conf3:
    print("  ✅ 无冲突")
for k in sorted(conf3)[:20]:
    print("  ⚠️ T.%-32s %s" % (k, sorted(conf3[k])))

print("\n=== 统计 ===")
print("window 名: %d（冲突 %d）" % (len(win_names), len(conf)))
print("setup 名 : %d（冲突 %d）" % (len(setup_names), len(conf2)))
print("T 名     : %d（冲突 %d）" % (len(t_names), len(conf3)))
