"""查 3 个 widget 参数不足是否误报。"""
import html
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"

NAMES = ["actionstentacleadvcheckbox", "babyRentDisplay", "whitneyRoofRuleBreak"]


def load(p):
    z = zipfile.ZipFile(p)
    return html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


mg = load(APK)
vg = load(VAN)

for n in NAMES:
    print("=" * 90)
    print(n)
    print("=" * 90)
    # widget 定义体
    m = re.search(r'<<widget\s+"' + re.escape(n) + r'"\s*>>(.*?)<</widget>>', mg, re.S)
    if m:
        body = m.group(1)
        idxs = sorted(set(int(x) for x in re.findall(r"_args\[(\d+)\]", body)))
        print(f"  定义用到的 _args 索引: {idxs}")
        print(f"  定义体前 400: {body[:400]!r}")
    else:
        print("  （modded 无定义）")

    print("\n  modded 调用:")
    for cm in list(re.finditer(r"<<" + re.escape(n) + r"\b", mg))[:6]:
        print(f"    {mg[cm.start():cm.start()+180]!r}")
    print("\n  vanilla 调用:")
    for cm in list(re.finditer(r"<<" + re.escape(n) + r"\b", vg))[:6]:
        print(f"    {vg[cm.start():cm.start()+180]!r}")
    print()
