"""Y04：修 Quoted Link Fix 的 8 处空 regexFlag（救回 8 个死链）。

背景：
  `Quoted Link Fix` 模组的补丁想修 `[[Next|"School Boy's Toilets"]]` 这种带引号的目标，
  但因为 `regexFlag: ""` 导致 new RegExp(p, "") 失败，补丁全部失效。
  于是那 8 个 link 目标一直是带引号的死链。

修法：删掉空的 regexFlag 字段（与 K17 修 DoLSims 同一手法）。
"""
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
    print("[Y04] index 形态异常")
    sys.exit(1)

g = H.unescape(data)
MARK = "[Y04]"
if MARK in g:
    print("[Y04] 已存在，跳过")
    sys.exit(0)

m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", g, re.S)
block_start, block_end = m.start(1), m.end(1)
block = m.group(1)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', block)

fixed_mods = []
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
            if not isinstance(p, dict):
                continue
            # 删掉所有空的 regexFlag
            if p.get("regexFlag") == "":
                del p["regexFlag"]
                changed += 1

    if not changed:
        continue

    print(f"  [{modname}] 删除空 regexFlag: {changed} 处")

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
    fixed_mods.append(modname)

if fixed_mods:
    data = data[:block_start] + new_block + data[block_end:]
    # 打标记
    data = data.replace(
        H.escape('<<widget "generateshoppage">>', quote=False),
        H.escape('<!-- [Y04] 空 regexFlag -->' + '<<widget "generateshoppage">>', quote=False), 1)
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"\n✅ 修了 {len(fixed_mods)} 个模组: {fixed_mods}")
else:
    print("\n⚠️ 没有需要修的")

# ---- 校验 ----
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

print(f"\n校验: 剩余空 regexFlag = {left}  {'OK' if left == 0 else 'FAIL'}")
print(f"passage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")
sys.exit(0 if left == 0 else 1)
