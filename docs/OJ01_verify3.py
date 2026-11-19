"""第 40 轮：核查 3 类真问题。"""
import html
import re
import zipfile

MODDED = r"E:\TAML\_dol\work\index_modded6.html"
VANILLA = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(path):
    if path.endswith(".apk"):
        z = zipfile.ZipFile(path)
        raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    else:
        raw = open(path, "rb").read().decode("utf-8", "replace")
    blocks = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        blocks[html.unescape(m.group(1))] = html.unescape(m.group(2))
    return blocks


mb = load(MODDED)
vb = load(VANILLA)

CASES = [
    ("Avery Valentines Missed Rage Fight Finish", r"\$bus"),
    ("Gwylan Ritual Sex Widgets", r"\$sexRitual\.bondage"),
    ("Mansion Bedroom Avery Dress", r"either\("),
]

for pn, pat in CASES:
    print("=" * 94)
    print(f"{pn}   ({pat})")
    print("=" * 94)
    for label, blocks in (("vanilla", vb), ("modded", mb)):
        b = blocks.get(pn, "")
        print(f"\n--- {label} (长度 {len(b)}) ---")
        for m in re.finditer(pat, b):
            seg = b[max(0, m.start() - 120):m.start() + 320]
            print(f"  @{m.start()}: {seg!r}")
            print()
    print()
