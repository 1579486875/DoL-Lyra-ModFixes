"""修 CSS class / 变量名被翻译破坏的问题。"""
import html as H
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"

CJK = re.compile(r"[\u4e00-\u9fff]")


def load_vanilla():
    z = zipfile.ZipFile(VAN)
    return H.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


def main():
    vg = load_vanilla()
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    g = H.unescape(data)

    print("=" * 90)
    print("1) class='settings头部er' 是什么")
    print("=" * 90)
    for m in re.finditer(r"settings头部er", g):
        print(f"  {g[max(0,m.start()-150):m.start()+150]!r}")
    print("\n  vanilla 里对应:")
    for m in list(re.finditer(r"settingsHeader", vg))[:3]:
        print(f"  {vg[max(0,m.start()-150):m.start()+150]!r}")

    print("\n" + "=" * 90)
    print("2) $featsBoosts.up成绩。newLife")
    print("=" * 90)
    for m in re.finditer(r"featsBoosts\.up成绩。newLife", g):
        print(f"  {g[max(0,m.start()-200):m.start()+200]!r}")
    print("\n  vanilla 里 featsBoosts.up:")
    for m in list(re.finditer(r"featsBoosts\.up\w*", vg))[:5]:
        print(f"  {vg[max(0,m.start()-150):m.start()+150]!r}")

    print("\n" + "=" * 90)
    print("3) gender_body 的对象键")
    print("=" * 90)
    for m in re.finditer(r"gender_body is \(\{", g):
        print(f"  {g[max(0,m.start()-100):m.start()+250]!r}")
    print("\n  vanilla:")
    for m in list(re.finditer(r"gender_body is \(\{", vg))[:2]:
        print(f"  {vg[max(0,m.start()-100):m.start()+250]!r}")

    print("\n" + "=" * 90)
    print("4) 所有 class= / id= 里的中文（详细）")
    print("=" * 90)
    for m in re.finditer(r'(?:class|id)="([^"]{0,200})"', g):
        v = m.group(1)
        if CJK.search(v):
            print(f"\n  {m.group(0)[:200]!r}")
            print(f"    上下文: {g[max(0,m.start()-120):m.start()+200]!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
