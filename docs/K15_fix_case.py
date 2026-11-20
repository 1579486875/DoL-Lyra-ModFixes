"""K15：修 DoLSims 补丁的 fallentransform 大小写。"""
import base64
import html as H
import io
import json
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    raise SystemExit("❌ index 形态异常")

g = H.unescape(data)
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", g, re.S)
block_start, block_end = m.start(1), m.end(1)
block = m.group(1)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', block)
print(f"模组 {len(parts)}\n")

fixed_total = 0
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

    changed = False
    for a in (bj.get("addonPlugin") or []):
        if not isinstance(a, dict) or a.get("addonName") != "TweeReplacerAddon":
            continue
        ps = a.get("params")
        if not isinstance(ps, list):
            continue
        for p in ps:
            if not isinstance(p, dict):
                continue
            for key in ("findString", "findRegex"):
                v = p.get(key)
                if not isinstance(v, str):
                    continue
                # 只改 widget 名，不改 $speechfallentransform 变量
                if 'widget "fallentransform"' in v:
                    nv = v.replace('widget "fallentransform"', 'widget "fallenTransform"')
                    p[key] = nv
                    changed = True
                    print(f"[{modname}] {key}")
                    print(f"  旧: {v[:150]!r}")
                    print(f"  新: {nv[:150]!r}")

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
    fixed_total += 1
    print(f"   ✅ {modname} 已修\n")

if fixed_total:
    data = data[:block_start] + new_block + data[block_end:]
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"✅ 修了 {fixed_total} 个模组")
else:
    print("⚠️ 没有需要修的")

# 校验
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", g2, re.S)
print("\n" + "=" * 90)
print("校验")
print("=" * 90)
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
            if not isinstance(p, dict):
                continue
            v = p.get("findString") or p.get("findRegex") or ""
            if "fallentransform" in str(v):
                print(f"  [{bj.get('name')}] {str(v)[:150]!r}")

print(f"\npassage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")
