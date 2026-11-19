"""替换 JS 运行时拼接的英文模板（导致「You have 一个阴道」这类混合）。

这些在 <script> 里，BE_bake 不会碰，必须手工替换。
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

# JS 字符串模板 -> 中文
PAIRS = [
    ('sentence += "You have ";', 'sentence += "你有";'),
    ('sentence += "on top of your ";', 'sentence += "，覆盖在你的";'),
    ('sentence += " eye lenses ";', 'sentence += " 隐形眼镜 ";'),
    ('`You have a library book due today.`', '`你今天有一本图书馆的书到期。`'),
    ('"You have a terrible epiphany. The abuse you\'ve endured can be ignored no longer."',
     '"你忽然惊觉。那些你一直忍受的虐待，再也无法被忽视了。"'),
    ('"Your innocence has been replaced by trauma."', '"你的纯真已被创伤取代。"'),
    ('"A profound sense of peace falls on your mind. You were upset a moment ago, but you can\'t remember why."',
     '"一股深沉的宁静笼罩你的心头。你刚才还很不安，却想不起是为了什么。"'),
    ('"Your innocence is on full display. Trauma will continue to accumulate and will return should you run out of innocence."',
     '"你的纯真毫无遮掩地显露着。创伤会持续累积，一旦纯真耗尽便会卷土重来。"'),
]


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    total = 0
    for old, new in PAIRS:
        for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
            if a in data:
                n = data.count(a)
                data = data.replace(a, b)
                total += n
                print(f"  ✅ {old[:60]!r}  ({n})")
                break
        else:
            print(f"  （未命中）{old[:60]!r}")

    print(f"\n合计 {total} 处")
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")

    g = H.unescape(data)
    print(f"\n'You have ' 残留: {g.count('You have ')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
