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

# 应用 patch
j = raw.find(b"[", raw.find(b"window.modDataValueZipList"))
k = raw.find(b"]", j)
parts = re.findall(r'"([A-Za-z0-9+/=\s]+)"', raw[j + 1:k].decode("utf-8", "replace"))
for s in parts:
    b = base64.b64decode(re.sub(r"\s+", "", s))
    if b[:2] != b"PK":
        continue
    zz = zipfile.ZipFile(io.BytesIO(b))
    if "boot.json" not in zz.namelist():
        continue
    bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
    for a in bj.get("addonPlugin") or []:
        if not isinstance(a, dict) or a.get("addonName") != "TweeReplacerAddon":
            continue
        for p in a.get("params") or []:
            if not isinstance(p, dict):
                continue
            ps = p.get("passage")
            if ps != "Widgets Settings" or ps not in passages:
                continue
            if p.get("replaceFile"):
                try:
                    rep = zz.read(p["replaceFile"]).decode("utf-8", "replace")
                except Exception:
                    continue
            else:
                rep = p.get("replace") or ""
            c = passages[ps]
            fs = p.get("findString")
            fr = p.get("findRegex")
            if fs is not None and fs in c:
                passages[ps] = c.replace(fs, rep) if p.get("all") else c.replace(fs, rep, 1)
            elif fr is not None:
                try:
                    rx = re.compile(fr)
                    if rx.search(c):
                        passages[ps] = rx.sub(lambda _: rep, c, count=0 if p.get("all") else 1)
                except Exception:
                    pass

body = passages["Widgets Settings"]
print("Widgets Settings 长度:", len(body))

# 用栈分析 if/else/elseif/endif
stack = []
issues = []
for mm in re.finditer(r"<<if\b|<<elseif\b|<<else>>|<</if>>", body):
    tok = mm.group(0)
    if tok.startswith("<<if"):
        stack.append(("if", mm.start()))
    elif tok.startswith("<<elseif"):
        if not stack:
            issues.append(("孤立 elseif", mm.start()))
    elif tok == "<<else>>":
        if not stack:
            issues.append(("孤立 else", mm.start()))
    else:  # <</if>>
        if not stack:
            issues.append(("孤立 /if", mm.start()))
        else:
            stack.pop()

print(f"未闭合 if: {len(stack)}")
print(f"孤立标签: {len(issues)}")
for kind, pos in issues[:10]:
    print(f"\n  ⚠ {kind} @{pos}")
    print("    ", repr(body[max(0, pos - 200):pos + 120]))
for kind, pos in stack[:5]:
    print(f"\n  ⚠ 未闭合 if @{pos}")
    print("    ", repr(body[max(0, pos - 150):pos + 250]))
