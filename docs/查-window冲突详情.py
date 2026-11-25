# -*- coding: utf-8 -*-
"""核查 5 个 window 冲突的实际赋值，判断是否真冲突。"""
import base64
import io
import json
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", h, re.S)

TARGETS = ["EdenCheats", "MirrorHypnoVariableRefresh", "createCafePC", "currentSkillValue", "mee"]
MODS_OF_INTEREST = ["FertilityExpansion", "MapleBirchCE", "DoLSims", "猫咖出租屋", "CombatSkills",
                    "more useful foodstuff", "露出拓展-请别露出惊讶的表情好吗"]

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
    if nm not in MODS_OF_INTEREST:
        continue
    for f in zz.namelist():
        if not f.lower().endswith(".js"):
            continue
        try:
            if zz.getinfo(f).file_size > 3_000_000:
                continue
            t = zz.read(f).decode("utf-8", "replace")
        except Exception:
            continue
        for tgt in TARGETS:
            for mm in re.finditer(r"window\." + re.escape(tgt) + r"\s*=", t):
                seg = t[max(0, mm.start() - 150):mm.start() + 350].replace("\n", " ")
                print("\n【%s】%s  window.%s" % (nm, f.split("/")[-1], tgt))
                print("  ", seg[:480])
