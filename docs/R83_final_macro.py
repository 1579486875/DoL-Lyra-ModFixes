import base64, html, io, json, re, zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
I18N = r"E:\TAML\_dol\work\i18n_dict.json"

data = open(HTML, "rb").read()
passages = {}
for m in re.finditer(rb'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', data, re.S):
    passages[m.group(1).decode("utf-8", "replace")] = html.unescape(m.group(2).decode("utf-8", "replace"))

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

j = data.find(b"[", data.find(b"window.modDataValueZipList"))
k = data.find(b"]", j)
parts = re.findall(r'"([A-Za-z0-9+/=\s]+)"', data[j + 1:k].decode("utf-8", "replace"))

patches = []
for s in parts:
    b = base64.b64decode(re.sub(r"\s+", "", s))
    if b[:2] != b"PK":
        continue
    zz = zipfile.ZipFile(io.BytesIO(b))
    if "boot.json" not in zz.namelist():
        continue
    bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
    name = bj.get("name") or "?"
    for f in bj.get("tweeFileList") or []:
        try:
            t = zz.read(f).decode("utf-8", "ignore")
        except Exception:
            continue
        for blk in re.split(r"(?m)^::\s*", t)[1:]:
            pn2 = blk.split("\n", 1)[0].strip()
            pn2 = re.sub(r"\s*\[[^\]]*\]\s*$", "", pn2)
            if pn2 and pn2 not in passages:
                passages[pn2] = blk[len(pn2):]
    for a in bj.get("addonPlugin") or []:
        if a.get("addonName") != "TweeReplacerAddon":
            continue
        for p in a.get("params") or []:
            patches.append((name, p, zz))

for name, p, zz in patches:
    ps = p.get("passage")
    if ps not in passages:
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

def strip_comments(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"/%.*?%/", "", s, flags=re.S)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    return s

PAIRS = [
    ("if", r"<<if\b", "<</if>>"),
    ("for", r"<<for\b", "<</for>>"),
    ("switch", r"<<switch\b", "<</switch>>"),
    ("widget", r"<<widget\b", "<</widget>>"),
    ("link", r"<<link\b", "<</link>>"),
    ("silently", r"<<silently\b", "<</silently>>"),
    ("capture", r"<<capture\b", "<</capture>>"),
]

print("=" * 92)
print("排除注释后的宏配对（应用全部补丁）")
print("=" * 92)
bad = 0
for pn, body in passages.items():
    b = strip_comments(body)
    for tag, op, cp in PAIRS:
        o = len(re.findall(op, b))
        c = b.count(cp)
        if o != c:
            bad += 1
            print(f"  [{pn}] {tag}: {o}/{c}  差 {o - c}")
print(f"\n真实异常: {bad}")
