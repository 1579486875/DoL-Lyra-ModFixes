"""第 10 轮：把 I18nLinkFix 的 10 条修复改为构建期直接注入（带负向断言，避免叠层）。

关键：修复后的文本包含原 findString 作为子串，
      必须用 (?!<) 断言确保只匹配「尚未闭合」的那一处。
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

FIXES = [
    ("Asylum Depths Tunnels 4 Swim",
     '<<link [[离开|Asylum Depths Tunnel 4 Leave]]>>',
     '<<link [[离开|Asylum Depths Tunnel 4 Leave]]>><</link>>'),
    ("Asylum Depths Tunnels 4 Return",
     '<<link [[离开|Asylum Depths Tunnel 4 Leave]]>>',
     '<<link [[离开|Asylum Depths Tunnel 4 Leave]]>><</link>>'),
    ("Fishing Moor Wait",
     '<<link [[回到荒原|Fishing Moor Hikers Drink Offer On PC Leave]]>>',
     '<<link [[回到荒原|Fishing Moor Hikers Drink Offer On PC Leave]]>><</link>>'),
    ("Livestock Barn Escape",
     '<<link [[走近河流|Livestock Barn Escape River]]>>',
     '<<link [[走近河流|Livestock Barn Escape River]]>><</link>>'),
    ("Livestock Tie Stall Punishment Farmhand Rape",
     '<<link [[继续|Livestock Tie Stall Punishment Farmhand Rape Finish]]>></link>',
     '<<link [[继续|Livestock Tie Stall Punishment Farmhand Rape Finish]]>><</link>>'),
    ("Livestock Tie Stall Punishment Cat Rape",
     '<<link [[继续|Livestock Tie Stall Punishment Cat Rape Finish]]>></link>',
     '<<link [[继续|Livestock Tie Stall Punishment Cat Rape Finish]]>><</link>>'),
    ("Livestock Tie Stall Punishment Cat Rape",
     '<<link [[继续|Livestock Tie Stall Punishment Cat Rape]]>></link>',
     '<<link [[继续|Livestock Tie Stall Punishment Cat Rape]]>><</link>>'),
    ("Livestock Cribbing Horse Deviancy Sex",
     '<<link [[继续|Livestock Cribbing Horse Deviancy Sex Finish]]>></link>',
     '<<link [[继续|Livestock Cribbing Horse Deviancy Sex Finish]]>><</link>>'),
    ("Livestock Cribbing Horse Deviancy Sex",
     '<<link [[继续|Livestock Cribbing Horse Deviancy Sex]]>></link>',
     '<<link [[继续|Livestock Cribbing Horse Deviancy Sex]]>><</link>>'),
    ("Police Cell",
     '<<if $stat_police.pillory gte 1>>还是个惯犯。”',
     '<<if $stat_police.pillory gte 1>>还是个惯犯。<</if>>”'),
]

DUP_ESC = "&gt;&gt;&lt;&lt;/link&gt;&gt;&lt;&lt;/link&gt;&gt;"
OK_ESC = "&gt;&gt;&lt;&lt;/link&gt;&gt;"


def fix_one(data, bad, good):
    """把 bad 替换成 good，但只在 bad 后面不是 < 时（即尚未闭合）。"""
    e_bad = H.escape(bad, quote=False)
    e_good = H.escape(good, quote=False)
    for pat, rep in ((re.escape(e_bad), e_good), (re.escape(bad), good)):
        # 负向断言：后面不能紧跟 '<'（避免匹配已闭合的）
        rx = re.compile(pat + r"(?!<)")
        if rx.search(data):
            return rx.sub(rep, data, count=1), True
    return data, False


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")

    n = data.count(DUP_ESC)
    if n:
        data = data.replace(DUP_ESC, OK_ESC)
        print(f"  预清理重复闭合: {n} 处")

    ok = 0
    fail = []
    for ps, bad, good in FIXES:
        data, hit = fix_one(data, bad, good)
        if hit:
            ok += 1
        else:
            fail.append((ps, bad[:60]))

    print(f"命中 {ok} / {len(FIXES)}")
    for ps, b in fail:
        print(f"  ❌ [{ps}] {b!r}")

    n2 = data.count(DUP_ESC)
    if n2:
        data = data.replace(DUP_ESC, OK_ESC)
        print(f"  后清理重复闭合: {n2} 处")

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
