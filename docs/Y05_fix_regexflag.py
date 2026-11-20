"""Y05：删除所有模组补丁里的空 regexFlag（幂等）。

空的 regexFlag 会让 new RegExp(pattern, "") 在某些实现下失败，整条补丁失效。
已知受影响：
  - DoLSims（K17 已修）
  - Quoted Link Fix（8 处，修好后能救回 8 个带引号的死链）
"""
import base64
import html as H
import io
import json
import os
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[Y05] index 形态异常")
    sys.exit(1)

g = H.unescape(data)
MARK = "[Y05]"
if MARK in g:
    print("[Y05] 已存在，跳过  passage=%d" % len(re.findall(r'<tw-passagedata[^>]*name=', data)))
    sys.exit(0)

m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", g, re.S)
if not m:
    print("[Y05] FAIL 找不到 modDataValueZipList")
    sys.exit(1)
block_start, block_end = m.start(1), m.end(1)
block = m.group(1)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', block)

fixed = []
new_block = block

for s in parts:
    raw = base64.b64decode(re.sub(r"\s+", "", s))
    if raw[:2] != b"PK":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(raw))
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
        modname = bj.get("name", "?")
    except Exception:
        continue

    changed = 0
    for a in (bj.get("addonPlugin") or []):
        if not isinstance(a, dict) or a.get("addonName") != "TweeReplacerAddon":
            continue
        for p in (a.get("params") or []):
            if isinstance(p, dict) and p.get("regexFlag") == "":
                del p["regexFlag"]
                changed += 1

    if not changed:
        continue

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
        for info in zz.infolist():
            d = zz.read(info.filename)
            if info.filename == "boot.json":
                d = json.dumps(bj, ensure_ascii=False, indent=2).encode("utf-8")
            zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            zi.compress_type = info.compress_type
            zi.external_attr = info.external_attr
            zo.writestr(zi, d)
    nb64 = base64.b64encode(buf.getvalue()).decode("ascii")
    pat = re.compile(r'"' + re.escape(s[:80]) + r'[A-Za-z0-9+/=\s]*"')
    new_block = pat.sub(lambda _: '"' + nb64 + '"', new_block, count=1)
    fixed.append((modname, changed))

if fixed:
    data = data[:block_start] + new_block + data[block_end:]
    data = data.replace(
        H.escape('<<widget "generateshoppage">>', quote=False),
        H.escape('<!-- [Y05] ' + "; ".join("%s×%d" % (m, c) for m, c in fixed) + ' -->'
                 + '<<widget "generateshoppage">>', quote=False), 1)
    open(HTML, "wb").write(data.encode("utf-8"))

# 校验
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", g2, re.S)
left = 0
for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m2.group(1)):
    try:
        d = base64.b64decode(re.sub(r"\s+", "", s))
        if d[:2] != b"PK":
            continue
        zz = zipfile.ZipFile(io.BytesIO(d))
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
    except Exception:
        continue
    for a in (bj.get("addonPlugin") or []):
        if not isinstance(a, dict) or a.get("addonName") != "TweeReplacerAddon":
            continue
        for p in (a.get("params") or []):
            if isinstance(p, dict) and p.get("regexFlag") == "":
                left += 1

ok = left == 0
print("[Y05] 修 %s  剩余空 regexFlag=%d  passage=%d  %s" % (
    fixed if fixed else "无",
    left,
    len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML, 'rb').read().decode('utf-8', 'replace'))),
    "OK" if ok else "FAIL"))
sys.exit(0 if ok else 1)
