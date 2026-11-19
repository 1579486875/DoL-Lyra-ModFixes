"""对比 vanilla 和 modded 的所有 CSS class 名，找被翻译的。"""
import html
import re
import zipfile
from collections import Counter

MOD = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"

CJK = re.compile(r"[\u4e00-\u9fff]")


def load(p):
    z = zipfile.ZipFile(p)
    return html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


mg = load(MOD)
vg = load(VAN)


def classes(g):
    """收集 class="a b c" 里的每个名字。"""
    out = Counter()
    for m in re.finditer(r'class\s*=\s*"([^"]*)"', g):
        for c in m.group(1).split():
            if c:
                out[c] += 1
    # 也收 class='...'
    for m in re.finditer(r"class\s*=\s*'([^']*)'", g):
        for c in m.group(1).split():
            if c:
                out[c] += 1
    return out


mc = classes(mg)
vc = classes(vg)

print(f"class 名: modded {len(mc)} / vanilla {len(vc)}")

print("\n" + "=" * 88)
print("含中文的 class 名（被翻译 → 样式失效）")
print("=" * 88)
bad = [(k, v) for k, v in mc.items() if CJK.search(k)]
print(f"  modded: {len(bad)} 种")
for k, n in sorted(bad, key=lambda x: -x[1])[:30]:
    print(f"    {k!r}  × {n}")
    for m in list(re.finditer(r'class\s*=\s*"[^"]*' + re.escape(k), mg))[:1]:
        print(f"      {mg[max(0,m.start()-100):m.start()+150]!r}")

vb = [(k, v) for k, v in vc.items() if CJK.search(k)]
print(f"\n  vanilla: {len(vb)} 种（应为 0）")

print("\n" + "=" * 88)
print("modded 独有的 class 名（找翻译残留）")
print("=" * 88)
only = sorted(set(mc) - set(vc), key=lambda x: -mc[x])
print(f"  {len(only)} 种")
for k in only[:30]:
    mark = "  ← 含中文" if CJK.search(k) else ""
    print(f"    {k!r} ×{mc[k]}{mark}")

print("\n" + "=" * 88)
print("vanilla 独有的 class 名（modded 丢失）")
print("=" * 88)
onlyv = sorted(set(vc) - set(mc), key=lambda x: -vc[x])
print(f"  {len(onlyv)} 种")
for k in onlyv[:25]:
    print(f"    {k!r} ×{vc[k]}")
