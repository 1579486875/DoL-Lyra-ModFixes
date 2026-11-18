import base64, html, io, json, re, zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
I18N = r"E:\TAML\_dol\work\i18n_dict.json"

z = zipfile.ZipFile(APK)
raw = z.read("assets/www/index.html")
passages = {}
for m in re.finditer(rb'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
    passages[m.group(1).decode("utf-8", "replace")] = html.unescape(m.group(2).decode("utf-8", "replace"))

# 应用 i18n
i18n = json.load(open(I18N, "r", encoding="utf-8"))
by_p = {}
for it in i18n["typeB"]["TypeBInputStoryScript"]:
    pn = it.get("pN")
    if pn:
        by_p.setdefault(pn, []).append(it)
for pn, lst in by_p.items():
    if pn not in passages:
        continue
    txt = passages[pn]
    for it in sorted(lst, key=lambda x: x.get("pos", 0), reverse=True):
        f, t = it.get("f"), it.get("t")
        if not f or t is None:
            continue
        pos = it.get("pos", -1)
        if 0 <= pos <= len(txt) and txt[pos:pos + len(f)] == f:
            txt = txt[:pos] + t + txt[pos + len(f):]
        elif f in txt:
            txt = txt.replace(f, t, 1)
    passages[pn] = txt

j = raw.find(b"[", raw.find(b"window.modDataValueZipList"))
k = raw.find(b"]", j)
parts = re.findall(r'"([A-Za-z0-9+/=\s]+)"', raw[j + 1:k].decode("utf-8", "replace"))

mods = []
for s in parts:
    b = base64.b64decode(re.sub(r"\s+", "", s))
    if b[:2] != b"PK":
        continue
    zz = zipfile.ZipFile(io.BytesIO(b))
    if "boot.json" not in zz.namelist():
        continue
    bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
    name = bj.get("name") or "?"
    mods.append((name, bj, zz))
    for f in bj.get("tweeFileList") or []:
        try:
            t = zz.read(f).decode("utf-8", "ignore")
        except Exception:
            continue
        for blk in re.split(r"(?m)^::\s*", t)[1:]:
            pn = blk.split("\n", 1)[0].strip()
            pn = re.sub(r"\s*\[[^\]]*\]\s*$", "", pn)
            if pn and pn not in passages:
                passages[pn] = blk[len(blk.split("\n", 1)[0]):]

print("passage 池:", len(passages))

missing_ps = []
miss_find = []
total = 0
for name, bj, zz in mods:
    for a in bj.get("addonPlugin") or []:
        if a.get("addonName") != "TweeReplacerAddon":
            continue
        for p in a.get("params") or []:
            total += 1
            ps = p.get("passage")
            if ps not in passages:
                missing_ps.append((name, ps))
                continue
            c = passages[ps]
            fs = p.get("findString")
            fr = p.get("findRegex")
            ok = False
            if fs is not None and fs in c:
                ok = True
            elif fr is not None:
                try:
                    rx = re.compile(fr)
                    ok = bool(rx.search(c))
                except Exception as e:
                    miss_find.append((name, ps, f"regex 非法: {e}"))
                    continue
            if not ok:
                miss_find.append((name, ps, (fs or fr or "")[:80]))

print(f"补丁总数: {total}")
print(f"passage 缺失: {len(missing_ps)}")
for n, ps in missing_ps[:10]:
    print(f"   ❌ [{n}] {ps}")
print(f"find 未命中: {len(miss_find)}")
print("=" * 92)
for n, ps, f in miss_find[:30]:
    print(f"  ❌ [{n}] {ps}")
    print(f"      {f!r}")
