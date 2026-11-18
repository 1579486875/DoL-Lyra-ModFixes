import base64, io, json, os, re, subprocess, tempfile, zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
raw = z.read("assets/www/index.html")
j = raw.find(b"[", raw.find(b"window.modDataValueZipList"))
k = raw.find(b"]", j)
parts = re.findall(r'"([A-Za-z0-9+/=\s]+)"', raw[j + 1:k].decode("utf-8", "replace"))

tmpdir = os.path.join(tempfile.gettempdir(), "doljs2")
os.makedirs(tmpdir, exist_ok=True)

print("=" * 92)
print("R11. JS 语法 + twee 结构")
print("=" * 92)

js_targets = []
twee_targets = []
for s in parts:
    b = base64.b64decode(re.sub(r"\s+", "", s))
    if b[:2] != b"PK":
        continue
    zz = zipfile.ZipFile(io.BytesIO(b))
    if "boot.json" not in zz.namelist():
        continue
    bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
    name = bj.get("name") or "?"
    for key in ("scriptFileList", "scriptFileList_inject_early", "scriptFileList_preload", "scriptFileList_earlyload"):
        for f in bj.get(key) or []:
            if f.endswith(".js"):
                try:
                    js_targets.append((name, f, zz.read(f).decode("utf-8", "ignore")))
                except Exception:
                    pass
    for f in bj.get("tweeFileList") or []:
        try:
            twee_targets.append((name, f, zz.read(f).decode("utf-8", "ignore")))
        except Exception:
            pass

print(f"JS 文件: {len(js_targets)}   twee 文件: {len(twee_targets)}")

js_err = []
for name, f, t in js_targets:
    p = os.path.join(tmpdir, "c.js")
    open(p, "w", encoding="utf-8").write(t)
    r = subprocess.run(["node", "--check", p], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        msg = (r.stderr or "").strip().split("\n")
        js_err.append((name, f, next((x for x in msg if "Error" in x), msg[0] if msg else "")))
print(f"\nJS 语法错误: {len(js_err)}")
for n, f, m in js_err[:10]:
    print(f"  ❌ [{n}] {f}\n      {m[:140]}")

PAIRS = [("if", r"<<if\b", "<</if>>"), ("for", r"<<for\b", "<</for>>"),
         ("switch", r"<<switch\b", "<</switch>>"), ("widget", r"<<widget\b", "<</widget>>"),
         ("link", r"<<link\b", "<</link>>"), ("silently", r"<<silently\b", "<</silently>>")]

tw_err = []
for name, f, t in twee_targets:
    tt = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    tt = re.sub(r"/%.*?%/", "", tt, flags=re.S)
    tt = re.sub(r"<!--.*?-->", "", tt, flags=re.S)
    for tag, op, cp in PAIRS:
        o = len(re.findall(op, tt))
        c = tt.count(cp)
        if o != c:
            tw_err.append((name, f, tag, o, c))
print(f"\ntwee 宏配对异常: {len(tw_err)}")
for n, f, tag, o, c in tw_err[:15]:
    print(f"  ⚠ [{n}] {f}  {tag}: {o}/{c}")
