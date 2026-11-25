# -*- coding: utf-8 -*-
"""逐个校验 index 里所有模组 ZIP 是否完好、boot.json 是否可解析。"""
import base64
import io
import json
import re
import zipfile

S = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(S, "rb").read().decode("utf-8", "replace")
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
ents = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', mz.group(1))
print("条目数:", len(ents))

bad = []
ok = 0
for i, s in enumerate(ents):
    try:
        d = base64.b64decode(re.sub(r"\s+", "", s))
    except Exception as e:
        bad.append((i, "base64", str(e)[:60]))
        continue
    if d[:2] != b"PK":
        print("  [%2d] 非 ZIP (%d 字节)" % (i, len(d)))
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(d))
        names = zz.namelist()
        # 校验每个条目可读
        for n in names:
            zz.read(n)
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
        ok += 1
    except Exception as e:
        bad.append((i, "zip/json", "%s: %s" % (type(e).__name__, str(e)[:80])))
        continue

print("\n✅ 完好: %d" % ok)
print("❌ 损坏: %d" % len(bad))
for b in bad:
    print("  ", b)

# 单独检查「系统联动补全」
print("\n=== 系统联动补全 详细 ===")
for s in ents:
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
    if (bj.get("name") or "") != "系统联动补全":
        continue
    print("ZIP 大小:", len(d))
    print("文件:", zz.namelist())
    for n in zz.namelist():
        info = zz.getinfo(n)
        print("  %-32s %7d" % (n, info.file_size))
    t = zz.read("scripts/core.js").decode("utf-8", "replace")
    print("core.js 长度:", len(t))
    # JS 语法粗检：括号配对
    print("  花括号: { =%d  } =%d" % (t.count("{"), t.count("}")))
    print("  圆括号: ( =%d  ) =%d" % (t.count("("), t.count(")")))
    print("  方括号: [ =%d  ] =%d" % (t.count("["), t.count("]")))
    break
