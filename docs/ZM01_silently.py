"""定位多余的 <</silently>>。"""
import html
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(p):
    z = zipfile.ZipFile(p)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    blocks = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        blocks[html.unescape(m.group(1))] = html.unescape(m.group(2))
    return blocks, html.unescape(raw)


mb, mg = load(APK)
vb, vg = load(VAN)

print("=" * 90)
print("逐 passage 对比 <<silently>> 配对")
print("=" * 90)
bad = []
for pn in mb:
    mo = len(re.findall(r"<<silently\b", mb[pn]))
    mc = mb[pn].count("<</silently>>")
    vo = len(re.findall(r"<<silently\b", vb.get(pn, "")))
    vc = vb.get(pn, "").count("<</silently>>")
    if mo != mc or (mo - mc) != (vo - vc):
        bad.append((pn, mo, mc, vo, vc))

for pn, mo, mc, vo, vc in bad:
    print(f"\n  [{pn}]  modded {mo}/{mc}  vanilla {vo}/{vc}")
    b = mb[pn]
    # 找所有 silently 的位置
    for m in re.finditer(r"<</silently>>", b):
        print(f"    </silently> @{m.start()}: {b[max(0,m.start()-200):m.start()+80]!r}")

print("\n" + "=" * 90)
print("全库找：没有任何 <<silently>> 的 passage 却有 <</silently>>")
print("=" * 90)
for pn, b in mb.items():
    if b.count("<</silently>>") > len(re.findall(r"<<silently\b", b)):
        print(f"  ❌ {pn}")
        for m in re.finditer(r"<</silently>>", b):
            print(f"    @{m.start()}: {b[max(0,m.start()-250):m.start()+100]!r}")
