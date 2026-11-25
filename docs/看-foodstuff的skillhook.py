# -*- coding: utf-8 -*-
"""看 more useful foodstuff 对 currentSkillValue 的完整包装，判断是否链式。"""
import base64
import io
import json
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", h, re.S)

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
    if (bj.get("name") or "") != "more useful foodstuff":
        continue
    for f in zz.namelist():
        if not f.lower().endswith(".js"):
            continue
        try:
            t = zz.read(f).decode("utf-8", "replace")
        except Exception:
            continue
        if "currentSkillValue" not in t:
            continue
        print("=== %s ===" % f)
        for mm in re.finditer(r"currentSkillValue", t):
            print("\n@%d:" % mm.start())
            print(t[max(0, mm.start() - 900):mm.start() + 400])
            break
        # 找那个函数完整定义
        m2 = re.search(r"function\s+(\w*[Ss]kill\w*)\s*\([^)]*\)\s*\{", t)
        if m2:
            start = t.index("{", m2.start())
            depth = 0
            i = start
            while i < len(t):
                if t[i] == "{":
                    depth += 1
                elif t[i] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                i += 1
            print("\n=== 完整函数 %s ===" % m2.group(1))
            print(t[m2.start():i + 1])
    break
