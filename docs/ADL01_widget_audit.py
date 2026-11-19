"""静态对比 modded vs vanilla 所有 widget passage 的 widget 数量。"""
import html
import re
import zipfile
from collections import Counter


def load(p):
    z = zipfile.ZipFile(p)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    blocks = {}
    tags = {}
    for m in re.finditer(r'<tw-passagedata([^>]*)>(.*?)</tw-passagedata>', raw, re.S):
        nm = re.search(r'name="([^"]+)"', m.group(1))
        tg = re.search(r'tags="([^"]*)"', m.group(1))
        if nm:
            pn = html.unescape(nm.group(1))
            blocks[pn] = html.unescape(m.group(2))
            tags[pn] = tg.group(1) if tg else ""
    return blocks, tags


MOD = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"

mb, mt = load(MOD)
vb, vt = load(VAN)

print(f"modded {len(mb)} passage / vanilla {len(vb)} passage")

mwp = {pn for pn, t in mt.items() if "widget" in t}
vwp = {pn for pn, t in vt.items() if "widget" in t}

print(f"widget passage: modded {len(mwp)} / vanilla {len(vwp)}")

print("\n" + "=" * 88)
print("widget 数量差异")
print("=" * 88)
diffs = []
for pn in sorted(mwp | vwp):
    a = len(re.findall(r'<<widget\s+"', mb.get(pn, "")))
    b = len(re.findall(r'<<widget\s+"', vb.get(pn, "")))
    if a != b:
        diffs.append((pn, a, b))
        print(f"  {pn:<40} modded {a:>3}  vanilla {b:>3}  差 {a-b:+d}")

if not diffs:
    print("  ✅ 无差异（除新加的 Widgets Repair）")

print("\n" + "=" * 88)
print("每个 passage 的 widget 结构配对")
print("=" * 88)
bad = []
for pn in sorted(mwp):
    b = mb.get(pn, "")
    o = len(re.findall(r"<<widget\b", b))
    c = b.count("<</widget>>")
    if o != c:
        bad.append((pn, o, c))
        print(f"  ❌ {pn}: {o}/{c} 差 {o-c}")
if not bad:
    print("  ✅ 全部配对")

print("\n" + "=" * 88)
print("widget 名集合差异（找 modded 缺失的）")
print("=" * 88)
mnames = set()
vnames = set()
for pn in mwp:
    mnames |= set(re.findall(r'<<widget\s+"([^"]+)"', mb.get(pn, "")))
for pn in vwp:
    vnames |= set(re.findall(r'<<widget\s+"([^"]+)"', vb.get(pn, "")))

only_v = sorted(vnames - mnames)
only_m = sorted(mnames - vnames)
print(f"  vanilla 有 modded 没有: {len(only_v)}")
if only_v:
    for x in only_v[:20]:
        # 找它在哪个 vanilla passage
        where = [pn for pn in vwp if f'<<widget "{x}"' in vb.get(pn, "")]
        print(f"    {x}  (vanilla: {where})")
print(f"\n  modded 有 vanilla 没有: {len(only_m)}")
for x in only_m[:10]:
    print(f"    {x}")

print("\n" + "=" * 88)
print("Check: modded 的每个 widget 是否在某个 passage 里（重复定义检查）")
print("=" * 88)
dups = []
for name in mnames:
    where = [pn for pn in mwp if f'<<widget "{name}"' in mb.get(pn, "")]
    if len(where) > 1:
        dups.append((name, where))
print(f"  重复定义的 widget: {len(dups)}")
for name, where in dups[:10]:
    print(f"    {name}: {where}")
