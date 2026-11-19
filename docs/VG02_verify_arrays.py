"""逐个核查 6 处中文数组比较，对照 vanilla 判断真假。"""
import html as H
import re

VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"
MOD = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
CJK = re.compile(r"[\u4e00-\u9fff]")


def load_apk(p):
    import zipfile
    z = zipfile.ZipFile(p)
    return H.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


vg = load_apk(VAN)
mg = load_apk(MOD)

TARGETS = [
    "黑狼",
    '"男孩"',
    '"亲爱的"',
    '"登山客"',
]

print("=" * 94)
print("1) 每个中文词在 vanilla 里的对应写法")
print("=" * 94)

# 黑狼 -> Black Wolf?
for kw, guess in [("黑狼", "Black Wolf"), ("男孩", "boy"), ("女孩", "girl"),
                  ("亲爱的", "darling"), ("登山客", "hiker"), ("混蛋", "bastard")]:
    n_kw = mg.count(f'"{kw}"')
    n_guess = vg.count(f'"{guess}"')
    print(f"\n  {kw!r}: modded {n_kw} 处  |  猜测 {guess!r}: vanilla {n_guess} 处")
    if n_guess:
        i = vg.find(f'"{guess}"')
        print(f"    vanilla 上下文: {vg[max(0,i-180):i+120]!r}")

print("\n" + "=" * 94)
print("2) modded 里这些数组的上下文")
print("=" * 94)
for m in re.finditer(r"\[([^\[\]]{1,200})\]\s*\.\s*(?:includes|indexOf)\s*\(([^)]{1,80})\)", mg):
    arr = m.group(1)
    if CJK.search(arr):
        print(f"\n  [{arr}].includes({m.group(2)})")
        print(f"    {mg[max(0,m.start()-250):m.start()+250]!r}")

print("\n" + "=" * 94)
print("3) vanilla 里对应的数组")
print("=" * 94)
for m in re.finditer(r"\[([^\[\]]{1,200})\]\s*\.\s*(?:includes|indexOf)\s*\(([^)]{1,80})\)", vg):
    arr = m.group(1)
    if any(k in arr for k in ("Sydney", "Ivory", "boy", "girl", "darling", "hiker")):
        print(f"\n  [{arr}].includes({m.group(2)})")
