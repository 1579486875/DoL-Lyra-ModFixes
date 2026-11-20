"""U04：确认 ramming 是正确词 + 看同组上下文。"""
import html as H
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
GOOD = r"E:\TAML\_dol\archive\DoL-Lyra-0.5.12.13-CHS-modded_20261120-061313_修复arsc可安装.apk"

g = H.unescape(zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace"))
gb = H.unescape(zipfile.ZipFile(GOOD).read("assets/www/index.html").decode("utf-8", "replace"))

print("=" * 90)
print("1. 词频对比")
print("=" * 90)
for kw in ("ramming", "rammal", "ramm", "冲撞"):
    print(f"  [{kw}]  当前={g.count(kw)}  基线={gb.count(kw)}")

print("\n" + "=" * 90)
print("2. $speechfencingentrance 上下文（看同组命名规律）")
print("=" * 90)
i = g.find("$speechfencingentrance")
if i > 0:
    print(repr(g[max(0, i - 600):i + 300]))

print("\n" + "=" * 90)
print("3. 目标行上下文")
print("=" * 90)
i = g.find("$speechrammalentrance")
if i > 0:
    print(repr(g[max(0, i - 800):i + 300]))

print("\n" + "=" * 90)
print("4. 该变量的读取处（有没有别处读它）")
print("=" * 90)
for kw in ("speechrammalentrance", "speech冲撞着entrance"):
    n_r = len(re.findall(r"\$" + re.escape(kw), g))
    n_b = len(re.findall(r"\$" + re.escape(kw), gb))
    print(f"  {kw!r}:  当前 {n_r}  基线 {n_b}")

print("\n" + "=" * 90)
print("5. speechfencing 是否也有 set（看是不是成对）")
print("=" * 90)
for kw in ("speechfencingentrance", "speechrammingentrance", "speechrammalentrance"):
    sets = len(re.findall(r"<<set\s+\$" + re.escape(kw) + r"\s+to", g))
    reads = len(re.findall(r"\$" + re.escape(kw), g))
    print(f"  {kw!r}:  set {sets} 次 / 总引用 {reads} 次")
