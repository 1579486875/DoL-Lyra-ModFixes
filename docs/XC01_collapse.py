"""折叠多层宏嵌套（兼容 HTML 转义形态）。

文件里是 &lt;&lt;NPC_CN_NAME ... &gt;&gt;
要折叠的是「同一个宏连续出现两次」的情况。
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

MACROS = ["NPC_CN_NAME", "NPC_CN_TITLE", "NPC_CN_TYPE", "BODYPARTS_CN_NAME"]


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    total = 0

    for macro in MACROS:
        for enc in (True, False):
            op = "&lt;&lt;" if enc else "<<"
            sp = " "
            needle = op + macro + sp
            # 反复删掉「紧邻重复」的那一层
            for _ in range(20):
                if (needle + needle) not in data:
                    break
                n = data.count(needle + needle)
                data = data.replace(needle + needle, needle)
                total += n
                print(f"  ✅ {macro}（{'转义' if enc else '原文'}）折叠 {n} 层")

    if total:
        open(HTML, "wb").write(data.encode("utf-8"))
        print(f"\n合计 {total} 层，写出 {HTML}")
    else:
        print("（无需折叠）")

    # 校验
    g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
    print("\n=== 校验 ===")
    for macro in MACROS:
        n = len(re.findall(re.escape(f"<<{macro} ") + re.escape(f"<<{macro} "), g))
        print(f"  {macro} 嵌套: {n}  {'✅' if n == 0 else '❌'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
