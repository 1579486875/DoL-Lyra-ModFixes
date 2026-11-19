"""第 43 轮：修原版 bug <<set $bus "avery_garage">>（缺 to）。

同一 passage 里另一处是 <<set $bus to "avery_bedroom">>（正确），
说明这处是原版手误。SugarCube 会把 `$bus "avery_garage"` 当非法表达式抛错，
导致后续 <<avery_mansion_end_links>> 不执行。
"""
import html as H
import os
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

OLD = '<<set $bus "avery_garage">>'
NEW = '<<set $bus to "avery_garage">>'


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    n = 0
    for a, b in ((H.escape(OLD, quote=False), H.escape(NEW, quote=False)), (OLD, NEW)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            n += c
            print(f"  ✅ 修复 {c} 处")
            break
    if not n:
        print("  （未命中）")

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")

    g = H.unescape(data)
    import re
    print(f"\n剩余 <<set $bus \"...\">> 缺 to: {len(re.findall(chr(60)*2 + 'set [^>]*?\$bus\\s+\"', g))}")
    print(f"正确的 <<set $bus to ...>>: {len(re.findall(chr(60)*2 + 'set [^>]*?\$bus\\s+to', g))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
