"""翻译最后 1 句残留英文剧情（Temple Forgiveness）。

[Widgets] "Expected a second parameter, but none was provided." 是 SugarCube 框架
内部错误信息，不翻译（翻了会让调试时看不懂）。
"""
import os
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

PAIRS = [
    ("That's a lot of money, but you can't think of any other way.",
     "那可是一大笔钱，但你想不出别的办法。"),
]


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    ok = 0
    for en, cn in PAIRS:
        for a, b in ((en, cn), (en.replace("'", "&#39;"), cn)):
            if a in data:
                n = data.count(a)
                data = data.replace(a, b)
                ok += 1
                print(f"  ✅ {en[:70]!r}  ({n} 处)")
                break
        else:
            print(f"  ❌ 未命中 {en[:70]!r}")

    print(f"\n命中 {ok} / {len(PAIRS)}")
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
