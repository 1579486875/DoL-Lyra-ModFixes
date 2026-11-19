"""按 passage 定位查 compoundWraith / avery_state / morethan1baby。"""
import html
import re
import zipfile


def load(p):
    z = zipfile.ZipFile(p)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    blocks = {}
    for m in re.finditer(r'<tw-passagedata([^>]*)>(.*?)</tw-passagedata>', raw, re.S):
        nm = re.search(r'name="([^"]+)"', m.group(1))
        if nm:
            blocks[html.unescape(nm.group(1))] = html.unescape(m.group(2))
    return blocks


MOD = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"

mb = load(MOD)
vb = load(VAN)

for var in ["compoundWraith", "avery_state", "morethan1baby"]:
    print("=" * 88)
    print(f"${var}")
    print("=" * 88)
    # 在 vanilla 找它所在的 passage
    where = [pn for pn, b in vb.items() if re.search(r"[$]" + re.escape(var) + r"\b", b)]
    print(f"  vanilla passage: {where}")
    for pn in where[:2]:
        print(f"\n  [vanilla {pn}]")
        m = re.search(r"[$]" + re.escape(var) + r"\b", vb[pn])
        if m:
            print(f"    {vb[pn][max(0,m.start()-250):m.start()+250]!r}")
        print(f"\n  [modded {pn}]")
        if pn in mb:
            # 打印同 passage 的对应片段（取相同位置附近）
            print(f"    {mb[pn][max(0,m.start()-250):m.start()+400]!r}")
        else:
            print("    (passage 不存在)")
    print()
