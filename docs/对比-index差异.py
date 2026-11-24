# -*- coding: utf-8 -*-
"""对比可用版本与当前 index 的差异，定位问题。"""
import re

GOOD = r"E:\TAML\_dol\work\index_from_good.apk.html"
CUR = r"E:\TAML\_dol\work\index_modded6.html"

g = open(GOOD, "rb").read().decode("utf-8", "replace")
c = open(CUR, "rb").read().decode("utf-8", "replace")

print("good: %d  cur: %d  差: %+d" % (len(g), len(c), len(c) - len(g)))

# 找第一处不同的位置
limit = min(len(g), len(c))
i = 0
while i < limit and g[i] == c[i]:
    i += 1
print("首个差异位置:", i)
print("  good 附近:", repr(g[max(0, i - 100):i + 150]))
print("  cur  附近:", repr(c[max(0, i - 100):i + 150]))

# 对比 modDataValueZipList 的条目数
for label, t in (("good", g), ("cur", c)):
    m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", t, re.S)
    if not m:
        print(label, "未找到数组")
        continue
    body = m.group(1)
    n = len(re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', body))
    print("%s: 数组体 %d 字符, 条目 %d" % (label, len(body), n))

# 对比模组名列表
import base64
import io
import json
import zipfile


def mod_names(t):
    m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", t, re.S)
    out = []
    for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1)):
        try:
            d = base64.b64decode(re.sub(r"\s+", "", s))
        except Exception:
            continue
        if d[:2] != b"PK":
            out.append("(non-zip %d)" % len(d))
            continue
        try:
            zz = zipfile.ZipFile(io.BytesIO(d))
            bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
            out.append(bj.get("name") or "?")
        except Exception:
            out.append("(bad zip)")
    return out


gn = mod_names(g)
cn = mod_names(c)
print("\ngood 模组:", len(gn))
print("cur  模组:", len(cn))
print("只在 good:", set(gn) - set(cn))
print("只在 cur :", set(cn) - set(gn))
