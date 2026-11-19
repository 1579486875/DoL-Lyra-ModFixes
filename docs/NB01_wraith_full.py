"""彻底修好 _speechWraith 的两处赋值。

现状（两处赋值点）：

A) Widgets Wraith 开头：
   <<set _speechWraith to "你_speak。\\"_line1 _line2\\"">>     ← 字面量
   <<set _speechWraith to "你_speak。\\"_line1\\"">>           ← 字面量

B) Widgets Wraith 结尾：
   <<set _speechWraith to "_speaks。" + "\\"" + "_line1" + _line2 + "\\"">>   ← "_line1" 是字符串
   <<set _speechWraith to "_speaks。\\"_line1\\"">>                          ← 字面量

目标（_line1 / _line2 是变量，要拼接）：
   <<set _speechWraith to "你_speak。\\"" + _line1 + _line2 + "\\"">>
   <<set _speechWraith to "你_speak。\\"" + _line1 + "\\"">>

   <<set _speechWraith to "_speaks。\\"" + _line1 + _line2 + "\\"">>
   <<set _speechWraith to "_speaks。\\"" + _line1 + "\\"">>
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

# 用正则宽松匹配，反斜杠数量不定
PATS = [
    # A1: 字面量 _line1 _line2
    (re.compile(r'<<set\s+_speechWraith\s+to\s+"(你_speak。)(\\*)"_line1 _line2(\\*)"">>'),
     lambda m: ('<<set _speechWraith to "' + m.group(1) + m.group(2) + '"' +
                ' + _line1 + _line2 + "' + m.group(3) + '">>')),
    # A2 / B2: 字面量 _line1（只有一个）
    (re.compile(r'<<set\s+_speechWraith\s+to\s+"((?:你)?_speak[s。]*)(\\*)"_line1(\\*)"">>'),
     lambda m: ('<<set _speechWraith to "' + m.group(1) + m.group(2) + '"' +
                ' + _line1 + "' + m.group(3) + '">>')),
    # B1: 已被 MH01 改过的 "_line1"（字符串而非变量）
    (re.compile(r'<<set\s+_speechWraith\s+to\s+"([^"]*?)(\\*)"\s*\+\s*"_line1"\s*\+\s*_line2\s*\+\s*"(\\*)">>'),
     lambda m: ('<<set _speechWraith to "' + m.group(1) + m.group(2) + '"' +
                ' + _line1 + _line2 + "' + m.group(3) + '">>')),
]


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    total = 0

    for pat, fn in PATS:
        # 未转义形态
        while True:
            m = pat.search(data)
            if not m:
                break
            data = data[:m.start()] + fn(m) + data[m.end():]
            total += 1
            print(f"  ✅ {fn(m)[:90]!r}")

        # 转义形态（&lt;&lt;set ... &gt;&gt;）
        esc = re.compile(
            pat.pattern.replace("<<set", "&lt;&lt;set")
                       .replace(">>", "&gt;&gt;")
                       .replace('"', '"')
        )
        while True:
            m = esc.search(data)
            if not m:
                break
            rep = H.escape(fn(m), quote=False)
            data = data[:m.start()] + rep + data[m.end():]
            total += 1
            print(f"  ✅ (转义) {fn(m)[:90]!r}")

    print(f"\n合计修复 {total} 处")

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")

    # 校验
    g = H.unescape(data)
    print("\n=== 校验 ===")
    for m in re.finditer(r"<<set\s+_speechWraith\s+to\s+[^>]*>>", g):
        s = m.group(0)
        bad = ('"_line1' in s and " + _line1" not in s) or "_line1 _" in s
        print(f"  {'❌' if bad else '✅'} {s[:110]!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
