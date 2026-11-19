"""A11：重写 Z03（不 escape 整文件）+ 跑 ZZ02 + Z03 + 验证。"""
import os
import re
import subprocess
import sys

WORK = r"E:\TAML\_dol\work"
HTML = os.path.join(WORK, "index_modded6.html")

NEW_Z03 = r'''"""Z03：修 FertilityExpansion 模组里未翻译的 NPC 名（明文直接改 base64，不 escape 整文件）。"""
import base64
import io
import json
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

# 安全阀
if len(re.findall(r"<tw-passagedata", data)) < 10000:
    print("[Z03] ❌ index 不是明文形态，拒绝修改")
    sys.exit(1)

m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", data, re.S)
if not m:
    print("[Z03] ❌ 无 modDataValueZipList")
    sys.exit(1)

block_start, block_end = m.start(1), m.end(1)
block = m.group(1)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', block)

TARGETS = [
    ("Bailey、Leighton 与 Gwylan 可按原版生理与怀孕规则参与受孕或授孕；Gwylan 的裸手牵手",
     "贝利、礼顿与格威岚可按原版生理与怀孕规则参与受孕或授孕；格威岚的裸手牵手"),
    ("Bailey、Leighton 与 Gwylan", "贝利、礼顿与格威岚"),
    ("Gwylan 的裸手牵手", "格威岚的裸手牵手"),
]

fixed = 0
new_block = block
for s in parts:
    raw = base64.b64decode(re.sub(r"\s+", "", s))
    if raw[:2] != b"PK":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(raw))
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
        if bj.get("name") != "FertilityExpansion":
            continue
    except Exception:
        continue

    buf = io.BytesIO()
    changed = []
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
        for info in zz.infolist():
            d = zz.read(info.filename)
            if info.filename.endswith((".twee", ".js", ".json", ".css", ".html", ".txt")):
                try:
                    txt = d.decode("utf-8")
                    orig = txt
                    for a, b in TARGETS:
                        if a in txt:
                            txt = txt.replace(a, b)
                    if txt != orig:
                        d = txt.encode("utf-8")
                        changed.append(info.filename)
                except Exception:
                    pass
            zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            zi.compress_type = info.compress_type
            zi.external_attr = info.external_attr
            zo.writestr(zi, d)

    if changed:
        new_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        # 在 block 里精确替换这个 base64（用首 80 字符定位）
        pat = re.compile(r'"' + re.escape(s[:80]) + r'[A-Za-z0-9+/=\s]*"')
        new_block2 = pat.sub(lambda _: '"' + new_b64 + '"', new_block, count=1)
        if new_block2 != new_block:
            new_block = new_block2
            fixed += len(changed)
            print("[Z03] 修 %s" % changed)

if fixed:
    data = data[:block_start] + new_block + data[block_end:]
    open(HTML, "wb").write(data.encode("utf-8"))

# 校验
g = open(HTML, "rb").read().decode("utf-8", "replace")
ok_pass = len(re.findall(r"<tw-passagedata", g)) > 10000
print("[Z03] 修 %d 个文件  passage=%d %s" % (
    fixed, len(re.findall(r"<tw-passagedata", g)), "OK" if ok_pass else "BROKEN"))

# 验证模组内容
m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", g, re.S)
if m2:
    for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m2.group(1)):
        raw = base64.b64decode(re.sub(r"\s+", "", s))
        if raw[:2] != b"PK":
            continue
        try:
            zz = zipfile.ZipFile(io.BytesIO(raw))
            bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
            if bj.get("name") != "FertilityExpansion":
                continue
            t = zz.read("game/eden-age.twee").decode("utf-8")
            ok = ("贝利、礼顿与格威岚" in t) and ("Bailey、Leighton 与 Gwylan" not in t)
            print("[Z03] 模组校验: %s" % ("OK" if ok else "FAIL"))
        except Exception:
            continue

sys.exit(0 if ok_pass else 1)
'''
open(os.path.join(WORK, "Z03_fix_mod_text.py"), "w", encoding="utf-8").write(NEW_Z03)
print("✅ Z03 已重写（不 escape）")

# 跑两个修复
print("\n" + "=" * 90)
print("跑 ZZ02")
print("=" * 90)
r = subprocess.run([sys.executable, os.path.join(WORK, "ZZ02_residue_fix.py")],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
print((r.stdout or "") + (r.stderr or ""))

print("=" * 90)
print("跑 Z03")
print("=" * 90)
r = subprocess.run([sys.executable, os.path.join(WORK, "Z03_fix_mod_text.py")],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
print((r.stdout or "") + (r.stderr or ""))

# 最终验证
print("=" * 90)
print("index 校验")
print("=" * 90)
g = open(HTML, "rb").read().decode("utf-8", "replace")
print(f"  明文 passage: {len(re.findall(r'<tw-passagedata', g))}")
print(f"  转义 passage: {len(re.findall(r'&lt;tw-passagedata', g))}")
print(f"  Tendrils of 深色ness: {g.count('Tendrils of 深色ness')}")
print(f"  黑暗的触须: {g.count('黑暗的触须')}")
print(f"  curvy:Curvy: {g.count('curvy: ' + chr(34) + 'Curvy' + chr(34))}")
print(f"  兽人类型 doggirl: {'doggirl' in g}")
