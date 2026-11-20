"""U02：查 $ene / $speech 丢失 + $speechrammalentrance 新增。"""
import html as H
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
GOOD = r"E:\TAML\_dol\archive\DoL-Lyra-0.5.12.13-CHS-modded_20261120-061313_修复arsc可安装.apk"

g = H.unescape(zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace"))
gb = H.unescape(zipfile.ZipFile(GOOD).read("assets/www/index.html").decode("utf-8", "replace"))

for kw in ("speechrammalentrance", "$ene", "$speech"):
    print("=" * 95)
    print(f"[{kw}]")
    print("=" * 95)
    for label, t in (("当前", g), ("基线", gb)):
        hs = list(re.finditer(re.escape(kw) if kw.startswith("$") else kw, t))
        print(f"  [{label}] {len(hs)} 处")
        for m in hs[:3]:
            print(f"    @{m.start()}: {t[max(0,m.start()-160):m.start()+220]!r}")
    print()

# 精确查 $ene 和 $speech 作为独立变量
print("=" * 95)
print("$ene 作为独立变量（后面不接字母）")
print("=" * 95)
for label, t in (("当前", g), ("基线", gb)):
    hs = re.findall(r"\$ene(?![A-Za-z0-9_])", t)
    print(f"  [{label}] {len(hs)} 处")

print("\n" + "=" * 95)
print("$speech 作为独立变量（后面不接字母）")
print("=" * 95)
for label, t in (("当前", g), ("基线", gb)):
    hs = re.findall(r"\$speech(?![A-Za-z0-9_])", t)
    print(f"  [{label}] {len(hs)} 处")
    for m in list(re.finditer(r"\$speech(?![A-Za-z0-9_])", t))[:3]:
        print(f"    @{m.start()}: {t[max(0,m.start()-150):m.start()+180]!r}")
