# -*- coding: utf-8 -*-
"""查 img/misc/icon/clothes/-peach-heart.png 的来源。"""
import base64
import io
import json
import re
import zipfile

APK = r"E:\TAML\_dol\out\育都孤儿-GNH个人整合版-2026.11.26.apk"
z = zipfile.ZipFile(APK)
h = z.read("assets/www/index.html").decode("utf-8", "replace")

print("=== 1) 包里有没有 peach-heart 相关的图 ===")
for n in z.namelist():
    if "peach" in n.lower() and "heart" in n.lower():
        print("   ", n)

print("\n=== 2) 包里 misc/icon/clothes 下以 - 开头的文件 ===")
cnt = 0
for n in z.namelist():
    base = n.rsplit("/", 1)[-1]
    if n.startswith("assets/www/img/misc/icon/clothes/") and base.startswith("-"):
        print("   ", n)
        cnt += 1
        if cnt >= 20:
            break
print("  共 %d 个（前20）" % cnt)

print("\n=== 3) index 里搜 peach-heart ===")
for mm in list(re.finditer(r"peach{0,2}heart|peach-heart", h, re.I))[:10]:
    print("  @%d: %s" % (mm.start(), h[max(0, mm.start() - 300):mm.start() + 200].replace("\n", " ")[:500]))

print("\n=== 4) 模组里搜 ===")
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
    nm = bj.get("name") or "?"
    for f in zz.namelist():
        if not f.lower().endswith((".js", ".json", ".twee", ".tw")):
            continue
        try:
            if zz.getinfo(f).file_size > 3_000_000:
                continue
            t = zz.read(f).decode("utf-8", "replace")
        except Exception:
            continue
        if "peach-heart" in t or "peachheart" in t.lower():
            print("\n【%s】%s" % (nm, f.split("/")[-1]))
            for mm in list(re.finditer(r"peach.?heart", t, re.I))[:3]:
                print("   @%d: %s" % (mm.start(), t[max(0, mm.start() - 300):mm.start() + 200].replace("\n", " ")[:450]))
