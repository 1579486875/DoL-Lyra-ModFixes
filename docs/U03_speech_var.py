"""U03：查 $speech*entrance / $speech* 系列变量的真名。"""
import html as H
import re
import zipfile
from collections import Counter

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
GOOD = r"E:\TAML\_dol\archive\DoL-Lyra-0.5.12.13-CHS-modded_20261120-061313_修复arsc可安装.apk"

g = H.unescape(zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace"))
gb = H.unescape(zipfile.ZipFile(GOOD).read("assets/www/index.html").decode("utf-8", "replace"))

print("=" * 95)
print("1. 所有 $speech*entrance 形态")
print("=" * 95)
for label, t in (("当前", g), ("基线", gb)):
    hs = Counter(re.findall(r"\$speech[A-Za-z\u4e00-\u9fff]*entrance", t))
    print(f"\n  [{label}] {len(hs)} 种")
    for k, v in hs.most_common(30):
        print(f"    {k!r} ×{v}")

print("\n" + "=" * 95)
print("2. 所有含中文的 $变量名（污染清单）")
print("=" * 95)
for label, t in (("当前", g), ("基线", gb)):
    hs = Counter(re.findall(r"\$[A-Za-z_][A-Za-z0-9_]*[\u4e00-\u9fff][A-Za-z0-9_\u4e00-\u9fff]*", t))
    print(f"\n  [{label}] {len(hs)} 种")
    for k, v in hs.most_common(30):
        print(f"    {k!r} ×{v}")

print("\n" + "=" * 95)
print("3. rammal 这个词的来历")
print("=" * 95)
for label, t in (("当前", g), ("基线", gb)):
    n = t.count("rammal")
    print(f"  [{label}] 'rammal' 出现 {n} 次")
    for m in list(re.finditer(r"rammal", t))[:5]:
        print(f"    @{m.start()}: {t[max(0,m.start()-150):m.start()+150]!r}")

print("\n" + "=" * 95)
print("4. 该 passage 的同类上下文（看同组变量怎么命名）")
print("=" * 95)
# 找 $speechXXXentrance 在上下 3000 字符内的同类
i = g.find("$speechrammalentrance")
if i > 0:
    seg = g[max(0, i - 4000):i + 4000]
    print("  当前包里该处附近的 $speech*：")
    for m in re.finditer(r"\$speech[A-Za-z]*", seg):
        print(f"    {m.group(0)!r}")
