"""查 pubnpc / compoundWraith / avery_state / morethan1baby / speech / ene 的下落。"""
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

CASES = ["pubnpc", "compoundWraith", "avery_state", "morethan1baby"]

for name in CASES:
    print("=" * 88)
    print(f"${name}")
    print("=" * 88)
    print("\n  [vanilla]")
    for m in list(re.finditer(r"\$" + re.escape(name) + r"\b", vg))[:3]:
        print(f"    {vg[max(0,m.start()-140):m.start()+140]!r}")
    print("\n  [modded 里搜相似]")
    # 找 modded 里含该词根的中文变量或文本
    stem = name.replace("_", "")
    found = 0
    for m in re.finditer(r"\$([\w\u4e00-\u9fff]*" + re.escape(name[:4]) + r"[\w\u4e00-\u9fff]*)", mg):
        print(f"    ${m.group(1)}: {mg[max(0,m.start()-100):m.start()+100]!r}")
        found += 1
        if found >= 3:
            break
    if not found:
        # 用 vanilla 的上下文去 modded 找对应位置
        m0 = re.search(r"\$" + re.escape(name), vg)
        if m0:
            anchor = vg[max(0, m0.start() - 60):m0.start()]
            # 取 anchor 里的英文词作线索
            print(f"    (modded 无相似变量名；vanilla 上下文锚点: {anchor[-60:]!r})")
    print()

print("=" * 88)
print("modded 独有: $speech / $ene")
print("=" * 88)
for name in ["speech", "ene"]:
    print(f"\n  ${name}:")
    for m in list(re.finditer(r"\$" + re.escape(name) + r"\b", mg))[:3]:
        print(f"    {mg[max(0,m.start()-140):m.start()+140]!r}")
    print(f"  vanilla 有 ${name}: {len(re.findall(r'[$]' + re.escape(name) + r'\\b', vg))} 处")
