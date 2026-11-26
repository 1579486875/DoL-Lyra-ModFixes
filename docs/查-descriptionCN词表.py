# -*- coding: utf-8 -*-
"""查 setup.description_CN 的实现与词表，看 rugged/slim/slight 有没有覆盖。"""
import base64
import io
import json
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", h, re.S)

print("=== index 里的 description_CN ===")
for mm in list(re.finditer(r"description_CN", h))[:3]:
    print("\n@%d: %s" % (mm.start(), h[max(0, mm.start() - 200):mm.start() + 500].replace("\n", " ")[:650]))

print("\n\n=== 模组里的 description_CN 定义 ===")
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
        m = re.search(r"description_CN\s*[:=]\s*function", t)
        if not m:
            continue
        start = m.start()
        print("\n【%s】%s @%d" % (nm, f.split("/")[-1], start))
        print(t[start:start + 2000])
        # 检查词表里有没有 rugged/slim/slight
        seg = t[start:start + 8000]
        for kw in ("rugged", "slim", "slight", "muscular", "lanky", "burly"):
            print("    %-10s %s" % (kw, "✅" if kw in seg else "❌"))
