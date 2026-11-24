# -*- coding: utf-8 -*-
"""扫包内实际模组（index_modded6.html 的 modDataValueZipList）里的玩家可见英文。
与 AUDIT_MOD_EN2.py 的区别：那个扫磁盘原始文件（含未安装的），这个扫打进包里的。
"""
import base64
import io
import json
import re
import zipfile
from collections import defaultdict

HTML = r"E:\TAML\_dol\work\index_modded6.html"
SENT = re.compile(r"\b[A-Za-z][A-Za-z']{2,}(?:\s+[A-Za-z][A-Za-z']{1,}){4,}\b")
SKIP = re.compile(r"^\s*(?:function|return|const|let|var|if|else|typeof|window|document|this)\b", re.I)


def strip_noise(txt):
    txt = re.sub(r"/\*.*?\*/", " ", txt, flags=re.S)
    txt = re.sub(r"<!--.*?-->", " ", txt, flags=re.S)
    txt = re.sub(r"^\s*//.*$", " ", txt, flags=re.M)
    txt = re.sub(r"<<.*?>>", " ", txt, flags=re.S)
    return txt


raw = open(HTML, "rb").read().decode("utf-8", "replace")
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)

hits = defaultdict(list)
n_mod = 0
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
    n_mod += 1
    nm = bj.get("name") or "?"
    for f in zz.namelist():
        if not f.lower().endswith((".twee", ".js")):
            continue
        try:
            if zz.getinfo(f).file_size > 3 * 1024 * 1024:
                continue
            t = zz.read(f).decode("utf-8", "replace")
        except Exception:
            continue
        clean = strip_noise(t)
        for mm in SENT.finditer(clean):
            line = mm.group(0).strip()
            if SKIP.match(line):
                continue
            # 去掉纯代码/路径
            if re.search(r"[{};=()\[\]]", line):
                continue
            hits[nm].append((f, line[:90]))

print("包内模组: %d 个\n" % n_mod)
print("=== 有英文句子的模组 ===")
total = 0
for nm in sorted(hits, key=lambda x: -len(hits[x])):
    arr = hits[nm]
    total += len(arr)
    print("\n[%s] %d 句" % (nm, len(arr)))
    seen = set()
    for f, line in arr:
        if f in seen:
            continue
        seen.add(f)
        print("   %s :: %s" % (f, line))
print("\n合计: %d 句" % total)
