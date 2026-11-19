"""精确修 B1：`"_speaks。" + "\\"" + "_line1" + _line2 + "\\""` 里的 "_line1" 是字符串。"""
import html as H
import os
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

OLD = '<<set _speechWraith to "_speaks。" + "\\"" + "_line1" + _line2 + "\\"">>'
NEW = '<<set _speechWraith to "_speaks。" + "\\"" + _line1 + _line2 + "\\"">>'


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")

    hit = 0
    for a, b in ((H.escape(OLD, quote=False), H.escape(NEW, quote=False)), (OLD, NEW)):
        if a in data:
            n = data.count(a)
            data = data.replace(a, b)
            hit += n
            print(f"  ✅ 替换 {n} 处")
            break

    if not hit:
        print("  ⚠️ 未命中，打印实际内容：")
        i = data.find("_speaks。")
        while i >= 0:
            seg = data[i:i + 200]
            if "_speechWraith" in data[max(0, i - 120):i]:
                print(f"      {seg!r}")
            i = data.find("_speaks。", i + 1)
        return 0

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")

    g = H.unescape(data)
    print("\n=== 最终校验 ===")
    for m in __import__("re").finditer(r"<<set\s+_speechWraith\s+to\s+[^>]*>>", g):
        s = m.group(0)
        bad = ('"_line1' in s and " + _line1" not in s) or "_line1 _" in s
        print(f"  {'❌' if bad else '✅'} {s[:110]!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
