"""查 printNobody / QUANTIFIER_OF_FOODS_CN / UPDATE_CLOTH_CN / temple_rank 在 vanilla 的原文。"""
import html
import re
import zipfile

MOD = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(p):
    z = zipfile.ZipFile(p)
    return html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


mg = load(MOD)
vg = load(VAN)

CASES = [
    ("printNobody", 'isGwylanAbsent() is "nobody"', "格威岚"),
    ("QUANTIFIER_OF_FOODS_CN", "QUANTIFIER_OF_FOODS", "数量词"),
    ("UPDATE_CLOTH_CN", "UPDATE_CLOTH", "衣物名"),
    ("temple_rank", "temple_rank", "神殿等级"),
]

for bad, anchor, desc in CASES:
    print("=" * 88)
    print(f"{bad!r}（{desc}）")
    print("=" * 88)

    # modded 里的调用上下文
    print("\n  [modded]")
    for m in list(re.finditer(r"<<" + re.escape(bad) + r"\b", mg))[:3]:
        print(f"    {mg[max(0,m.start()-150):m.start()+150]!r}")

    # vanilla 里对应的位置（用 anchor 找）
    print("\n  [vanilla 同 anchor]")
    for m in list(re.finditer(re.escape(anchor), vg))[:3]:
        print(f"    {vg[max(0,m.start()-200):m.start()+250]!r}")
    print()
