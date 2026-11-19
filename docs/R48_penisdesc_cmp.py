"""第 48 轮：对比 vanilla 与 modded 的 penisdisc.includes 判断。"""
import html
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(p):
    z = zipfile.ZipFile(p)
    return html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


mg = load(APK)
vg = load(VAN)

print("=" * 90)
print("1) vanilla 里 penisdisc.includes(...) 的所有参数值")
print("=" * 90)
from collections import Counter
vc = Counter(m.group(1) for m in re.finditer(r'penisdesc\.includes\(\s*"([^"]*)"\s*\)', vg))
for v, n in vc.most_common(20):
    print(f"  {n:>3}× {v!r}")

print("\n" + "=" * 90)
print("2) modded 里同样的")
print("=" * 90)
mc = Counter(m.group(1) for m in re.finditer(r'penisdesc\.includes\(\s*"([^"]*)"\s*\)', mg))
for v, n in mc.most_common(20):
    print(f"  {n:>3}× {v!r}")

print("\n" + "=" * 90)
print("3) penisDescList 的定义（human 列表）")
print("=" * 90)
for label, g in (("modded", mg), ("vanilla", vg)):
    print(f"\n[{label}]")
    for m in re.finditer(r"penisDescList\s*=\s*\{", g):
        seg = g[m.start():m.start() + 2000]
        print(f"  {seg[:1200]!r}")
        break
    else:
        # 找定义处
        for m in re.finditer(r"penisDescList", g):
            print(f"  @{m.start()}: {g[max(0,m.start()-100):m.start()+400]!r}")
            break

print("\n" + "=" * 90)
print("4) npcHasStrapon 函数")
print("=" * 90)
for label, g in (("modded", mg), ("vanilla", vg)):
    m = re.search(r"function npcHasStrapon\([^)]*\)\s*\{(.{0,500})", g)
    if m:
        print(f"\n[{label}] {m.group(0)[:600]!r}")
    else:
        print(f"\n[{label}] (未找到 function 定义)")
        for mm in list(re.finditer(r"npcHasStrapon", g))[:2]:
            print(f"  @{mm.start()}: {g[max(0,mm.start()-80):mm.start()+200]!r}")
