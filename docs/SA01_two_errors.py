"""查 setup.description_CN 和 wTimerProgress 两个报错。"""
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
print("1) setup.description_CN 引用点")
print("=" * 94)
for m in list(re.finditer(r"setup\.description_CN", g))[:6]:
    print(f"@{m.start()}: {g[max(0,m.start()-200):m.start()+250]!r}")
    print()

print("=" * 94)
print("2) setup.description_CN 是否被定义")
print("=" * 94)
defs = re.findall(r"setup\.description_CN\s*=", g)
print(f"  定义: {len(defs)} 处")

print("\n" + "=" * 94)
print("3) <<wTimerProgress>> 引用点")
print("=" * 94)
for m in list(re.finditer(r"wTimerProgress", g))[:6]:
    print(f"@{m.start()}: {g[max(0,m.start()-200):m.start()+250]!r}")
    print()

print("=" * 94)
print("4) wTimerProgress widget 定义")
print("=" * 94)
d = re.findall(r'<<widget\s+"wTimerProgress"', g)
print(f"  定义: {len(d)} 处")

print("\n" + "=" * 94)
print("5) 模组里有没有 wTimerProgress")
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
    for f in (bj.get("tweeFileList") or []) + (bj.get("scriptFileList") or []):
        try:
            t = zz.read(f).decode("utf-8", "ignore")
        except Exception:
            continue
        if "wTimerProgress" in t:
            for m in list(re.finditer("wTimerProgress", t))[:2]:
                print(f"  [{name}] {f}")
                print(f"    {t[max(0,m.start()-150):m.start()+250]!r}")
