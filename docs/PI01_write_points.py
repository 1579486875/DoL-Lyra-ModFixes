"""找所有往 setup.faceVariantOptions 写入的地方（模组 JS / 运行时）。"""
import base64
import html
import io
import json
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
raw = z.read("assets/www/index.html")
g = html.unescape(raw.decode("utf-8", "replace"))

print("=" * 94)
print("1) index 里的所有 faceVariantOptions 引用")
print("=" * 94)
for m in re.finditer(r"faceVariantOptions", g):
    ctx = g[max(0, m.start() - 120):m.start() + 180]
    print(f"@{m.start()}: {ctx!r}")
    print()

print("=" * 94)
print("2) 模组 JS 里的 faceVariantOptions / makeup 写入")
print("=" * 94)
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
    name = bj.get("name") or "?"
    for f in (bj.get("scriptFileList") or []) + (bj.get("tweeFileList") or []):
        try:
            t = zz.read(f).decode("utf-8", "ignore")
        except Exception:
            continue
        if "faceVariantOptions" in t or ("makeup" in t and "face" in t.lower()):
            for m in list(re.finditer(r"faceVariantOptions", t))[:3]:
                print(f"  [{name}] {f}")
                print(f"    {t[max(0,m.start()-160):m.start()+260]!r}")
                print()
