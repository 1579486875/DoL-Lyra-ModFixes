# -*- coding: utf-8 -*-
"""查 currentSkillValue 冲突两方的加载顺序与 hook 细节。"""
import base64
import io
import json
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", h, re.S)

order = []
for idx, s in enumerate(re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', mz.group(1))):
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
    order.append((idx, nm, zz, bj))

print("=== 关注模组在 index 中的位置 ===")
for idx, nm, zz, bj in order:
    if nm in ("CombatSkills", "more useful foodstuff"):
        print("  index[%d] %s" % (idx, nm))

# 各自的 hook 实现细节
print("\n" + "=" * 70)
print("=== hook 实现细节 ===")
print("=" * 70)
for idx, nm, zz, bj in order:
    if nm not in ("CombatSkills", "more useful foodstuff"):
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
        for mm in re.finditer(r"window\.currentSkillValue\s*=", t):
            print("\n【%s】%s  @%d" % (nm, f.split("/")[-1], mm.start()))
            print(t[max(0, mm.start() - 1400):mm.start() + 200])
