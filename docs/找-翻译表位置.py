# -*- coding: utf-8 -*-
"""找 dogboys,狗男 这个翻译表的位置与变量名。"""
import base64
import io
import json
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")

KEY = "dogboys,狗男"
hits = list(re.finditer(re.escape(KEY), h))
print("index 里命中 %d 处" % len(hits))
for mm in hits[:2]:
    print("\n@%d 上下文:" % mm.start())
    print(h[max(0, mm.start() - 900):mm.start() + 400].replace("\n", " ")[:1300])

# 找表变量名
print("\n=== 往前找赋值 ===")
if hits:
    before = h[max(0, hits[0].start() - 3000):hits[0].start()]
    for m in re.finditer(r"([\w\.\$]+)\s*=\s*[\"']", before):
        pass
    # 找最近的 = 后面跟 " 的
    cands = list(re.finditer(r"([A-Za-z_$][\w$\.]{2,40})\s*=\s*\"", before))
    for c in cands[-6:]:
        print("  ", c.group(1), "@", c.start())

# 模组里搜
print("\n=== 模组里搜 ===")
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
        if not f.lower().endswith((".js", ".twee", ".tw")):
            continue
        try:
            if zz.getinfo(f).file_size > 5_000_000:
                continue
            t = zz.read(f).decode("utf-8", "replace")
        except Exception:
            continue
        if KEY in t:
            i = t.find(KEY)
            print("\n【%s】%s @%d" % (nm, f.split("/")[-1], i))
            print("  ", t[max(0, i - 900):i + 400].replace("\n", " ")[:1300])
