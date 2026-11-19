"""扫全库「中文宏名」（<<中文>>），这是翻译破坏宏名的严重问题。"""
import html
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"

CJK = re.compile(r"[\u4e00-\u9fff]")


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
print("中文宏名（<<中文xxx>>）")
print("=" * 90)
hits = []
for pn, b in mb.items():
    for m in re.finditer(r"<<([\u4e00-\u9fff][^>]{0,60})>>", b):
        hits.append((pn, m.group(1), m.start()))

print(f"共 {len(hits)} 处")
seen = set()
for pn, name, pos in hits[:40]:
    key = (pn, name)
    if key in seen:
        continue
    seen.add(key)
    print(f"\n  [{pn}] <<{name[:50]}>>")
    b = mb[pn]
    print(f"    {b[max(0,pos-180):pos+150]!r}")

print("\n" + "=" * 90)
print("vanilla 里对应位置")
print("=" * 90)
for pn, name, pos in hits[:8]:
    if pn not in vb:
        continue
    # 在 vanilla 同 passage 找相似的上下文
    b = mb[pn]
    ctx = b[max(0, pos - 80):pos + 20]
    # 取前 20 个字符作为锚
    anchor = ctx[:30]
    print(f"\n  [{pn}] 中文宏 <<{name[:30]}>>")
    print(f"    modded: {b[max(0,pos-150):pos+120]!r}")
    print(f"    vanilla 同 passage 前 400: {vb[pn][:400]!r}")
