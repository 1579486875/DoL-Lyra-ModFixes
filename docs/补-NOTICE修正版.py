# -*- coding: utf-8 -*-
"""给 CombatSkills / LocationsExt / CombatActionsExt 补回作者的 NOTICE.md 与 LICENSE（修正版）。"""
import base64
import io
import json
import re
import sys
import urllib.request
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
TARGETS = {"CombatSkills", "LocationsExt", "CombatActionsExt"}
REPO = "1KMJTIO194/dol-combat-skills"


def gh_raw(path):
    url = "https://api.github.com/repos/%s/contents/%s" % (REPO, path)
    req = urllib.request.Request(url, headers={"User-Agent": "dsh", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        j = json.loads(r.read().decode())
    return base64.b64decode(j["content"]).decode("utf-8")


LICENSE_TXT = gh_raw("LICENSE")
NOTICE_TXT = gh_raw("NOTICE.md")
print("LICENSE  %d 字节 | NOTICE %d 字节" % (len(LICENSE_TXT.encode()), len(NOTICE_TXT.encode())))

raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
entries = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1))
print("数组条目:", len(entries))

changed = 0
new_raw = raw

for s in entries:
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
    nm = bj.get("name") or ""
    if nm not in TARGETS:
        continue

    names = zz.namelist()
    has_lic = any(x.upper().startswith("LICENSE") for x in names)
    has_notice = any("NOTICE" in x.upper() for x in names)
    print("\n【%s】LICENSE=%s NOTICE=%s" % (nm, has_lic, has_notice))

    if has_lic and has_notice:
        print("  已齐全，跳过")
        continue

    # 收集现有文件（内存里）
    files = []
    for info in zz.infolist():
        files.append((info, zz.read(info.filename)))

    # 更新 boot.json
    bj2 = dict(bj)
    arr = bj2.get("additionFile")
    if not isinstance(arr, list):
        arr = []
    for f in ("LICENSE", "NOTICE.md"):
        if f not in arr:
            arr.append(f)
    bj2["additionFile"] = arr
    new_boot = json.dumps(bj2, ensure_ascii=False, indent=2).encode("utf-8")

    # 重建
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zo:
        for info, data in files:
            if info.filename == "boot.json":
                continue  # 稍后重写
            zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            zi.compress_type = info.compress_type
            zi.external_attr = info.external_attr
            zo.writestr(zi, data)
        zo.writestr("boot.json", new_boot)
        if not has_lic:
            zo.writestr("LICENSE", LICENSE_TXT.encode("utf-8"))
            print("  + LICENSE")
        if not has_notice:
            zo.writestr("NOTICE.md", NOTICE_TXT.encode("utf-8"))
            print("  + NOTICE.md")

    final = out.getvalue()   # ← 在 with 块外取 OK，因为 out 没 close

    new_b64 = base64.b64encode(final).decode("ascii")
    new_raw = new_raw.replace(s, new_b64, 1)
    changed += 1
    print("  新 ZIP: %d 字节" % len(final))

print("\n处理模组:", changed)
if changed == 0:
    sys.exit(0)

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', new_raw))
m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", new_raw, re.S)
n_b = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', m.group(1)))
n_a = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', m2.group(1)))
print("passage:", npass, "->", npass2, "| 条目:", n_b, "->", n_a)
if npass2 != npass or n_b != n_a:
    print("❌ 校验失败")
    sys.exit(1)

open(HTML, "wb").write(new_raw.encode("utf-8"))
print("✅ 写入")

# 复核
print("\n=== 复核 ===")
m3 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", new_raw, re.S)
for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m3.group(1)):
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
    if (bj.get("name") or "") not in TARGETS:
        continue
    names = zz.namelist()
    print("【%s】%s" % (bj.get("name"), [x for x in names if "LICEN" in x.upper() or "NOTICE" in x.upper()]))
