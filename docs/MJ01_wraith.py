"""修 Wraith 的 _speechWraith 字符串（i18n 把拼接改成了字面量）。

实际现状：
  <<set _speechWraith to "你_speak。\"_line1 _line2\"">>
  <<set _speechWraith to "你_speak。\"_line1\"">>

期望：
  <<set _speechWraith to "你_speak。\"" + "_line1" + _line2 + "\"">>

脚本容错：找不到就跳过并 return 0，不阻断构建。
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    orig = data

    # 形态 A："_line1 _line2"  ->  "_line1" + _line2
    pats = [
        # 未转义
        (re.compile(r'<<set\s+_speechWraith\s+to\s+"([^"]*?)_line1 _line2(\\*)"">>'),
         lambda m: '<<set _speechWraith to "' + m.group(1) + '_line1" + _line2 + "' + m.group(2) + '">>'),
        # 转义 &lt;&lt;
        (re.compile(r'&lt;&lt;set\s+_speechWraith\s+to\s+"([^"]*?)_line1 _line2(\\*)"">&gt;&gt;'),
         lambda m: H.escape('<<set _speechWraith to "' + m.group(1) + '_line1" + _line2 + "' + m.group(2) + '">>',
                            quote=False)),
    ]

    n = 0
    for pat, fn in pats:
        while True:
            m = pat.search(data)
            if not m:
                break
            data = data[:m.start()] + fn(m) + data[m.end():]
            n += 1

    if n:
        print(f"✅ 修复 _speechWraith 字面量 _line2: {n} 处")
    else:
        print("（无匹配，跳过）")

    if data != orig:
        open(HTML, "wb").write(data.encode("utf-8"))

    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")
    return 0  # 永远成功，不阻断构建


if __name__ == "__main__":
    sys.exit(main())
