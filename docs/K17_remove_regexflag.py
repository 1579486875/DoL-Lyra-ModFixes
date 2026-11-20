"""K17：尝试去掉 DoLSims 补丁的 regexFlag:"" 字段。"""
import base64
import html as H
import io
import json
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

g = H.unescape(data)
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", g, re.S)
block_start, block_end = m.start(1), m.end(1)
block = m.group(1)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', block)

fixed = 0
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
    if modname != "DoLSims":
        continue

    changed = 0
    for a in (bj.get("addonPlugin") or []):
        if not isinstance(a, dict) or a.get("addonName") != "TweeReplacerAddon":
            continue
        for p in (a.get("params") or []):
            if not isinstance(p, dict):
                continue
            # 删掉空的 regexFlag
            if p.get("regexFlag") == "":
                del p["regexFlag"]
                changed += 1
            # 也删掉空的其他可选字段
            for k in ("debug", "all", "comments", "_comment1"):
                if k in p and p[k] in ("", None):
                    del p[k]

    if not changed:
        continue

    print(f"[{modname}] 删除空 regexFlag: {changed} 处")

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
    fixed += 1

if fixed:
    data = data[:block_start] + new_block + data[block_end:]
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"\n✅ 已写入")
else:
    print("⚠️ 没有需要改的")

# 校验
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print(f"\npassage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")
m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", g2, re.S)
for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m2.group(1)):
    try:
        d = base64.b64decode(re.sub(r"\s+", "", s))
        if d[:2] != b"PK":
            continue
        zz = zipfile.ZipFile(io.BytesIO(d))
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
    except Exception:
        continue
    if bj.get("name") != "DoLSims":
        continue
    n_empty = 0
    for a in (bj.get("addonPlugin") or []):
        if not isinstance(a, dict) or a.get("addonName") != "TweeReplacerAddon":
            continue
        for p in (a.get("params") or []):
            if isinstance(p, dict) and p.get("regexFlag") == "":
                n_empty += 1
    print(f"  DoLSims 剩余空 regexFlag: {n_empty}")
