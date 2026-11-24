# -*- coding: utf-8 -*-
"""扫描所有模组 JS/JS 与全局系统之间的交叉调用，找出真实联动。"""
import base64
import io
import json
import re
import zipfile
from collections import defaultdict

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
raw = z.read("assets/www/index.html").decode("utf-8", "replace")
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)

# 全局系统标识
SYSTEMS = {
    "BasicNeeds": [r"\bBasicNeeds\b", r"window\.BN\b", r"\bbnSettle", r"\bbnMood"],
    "暴露(mee)": [r"window\.mee\b", r"\bmee\.", r"getexcretes", r"\bexposure\b"],
    "生育": [r"\bpregnan", r"\bFertilityExpansion\b", r"\bFertility\b"],
    "手机": [r"\bPhone\b", r"\bsmartphone\b", r"TaskDanger"],
    "房产/金融": [r"maplebirch\.get\(\"Finance\"\)", r"\brealEstate\b", r"\bFinance\b"],
    "战斗": [r"\benemyarousal\b", r"\bCombatSkills\b", r"\bcombat\b"],
    "服装": [r"\$worn\b", r"\bgetClothingOptions\b", r"\bworn\."],    "暴露度变量": [r"\$exposure\b", r"\bexhibitionism\b"],
    "转化": [r"\$transformations\b", r"\btfParts\b", r"\btransformationParts\b"],
    "时间": [r"\bTime\.pass\b", r"\bTime\.date\b", r"\bTime\.time"],
    "NPC关系": [r"\bNPCList\b", r"\baffection\b", r"\bdom\b"],
    "地点": [r"\bLocationsExt\b", r"\bmaplebirch\.get\(\"Locations\"\)"],
    "作弊": [r"\bcheat\b", r"\bMapleBirchCE\b"],
}

mod_hits = defaultdict(lambda: defaultdict(int))

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
    nm = bj.get("name") or "?"
    # 读所有 js / twee
    text = ""
    for f in zz.namelist():
        if not f.lower().endswith((".js", ".twee")):
            continue
        try:
            if zz.getinfo(f).file_size > 6 * 1024 * 1024:
                continue
            text += zz.read(f).decode("utf-8", "replace") + "\n"
        except Exception:
            pass
    if not text:
        continue
    for sysname, pats in SYSTEMS.items():
        c = 0
        for p in pats:
            c += len(re.findall(p, text))
        if c:
            mod_hits[nm][sysname] = c

# 输出矩阵
print("=== 模组 × 系统 引用矩阵（数字=出现次数）===")
all_sys = list(SYSTEMS)
print("%-32s %s" % ("模组", " ".join("%-10s" % s[:10] for s in all_sys)))
for nm in sorted(mod_hits, key=lambda x: -sum(mod_hits[x].values())):
    row = []
    for s in all_sys:
        v = mod_hits[nm].get(s, 0)
        row.append("%-10s" % (v if v else "-"))
    print("%-32s %s" % (nm, " ".join(row)))

# 每个系统被几个模组碰
print("\n=== 每个系统被多少个模组引用 ===")
for s in all_sys:
    n = sum(1 for nm in mod_hits if mod_hits[nm].get(s))
    users = [nm for nm in mod_hits if mod_hits[nm].get(s)]
    print("  %-14s %2d 个模组: %s" % (s, n, ", ".join(sorted(users)[:8])))
