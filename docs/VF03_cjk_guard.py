"""中文标识符守卫（并入 build_all）。

检查并修复三类「翻译破坏代码逻辑」：
  1) $obj.纯中文属性         -> 用 vanilla 对照还原
  2) 中文数组做 includes 比较 -> 只修系统值的（Weather / NPCNameList）
  3) 已知清单兜底
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
CJK = re.compile(r"[\u4e00-\u9fff]")

# 明确的修复清单（每一条都经 vanilla 对照确认）
FIXES = [
    ("$avery_mansion.鞠躬", "$avery_mansion.bow"),
    ("$attitudesControl.unlockAvery鞠躬", "$attitudesControl.unlockAveryBow"),
    ('["Sydney", "黑狼", "Ivory Wraith"]', '["Sydney", "Black Wolf", "Ivory Wraith"]'),
    ('["下雨", "下雪"]', '["rain", "snow"]'),
    ('["下雪", "下雨"]', '["snow", "rain"]'),
    ('["下雨","下雪"]', '["rain","snow"]'),
    ('["下雪","下雨"]', '["snow","rain"]'),
]


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    total = 0
    for old, new in FIXES:
        if old in data:
            n = data.count(old)
            data = data.replace(old, new)
            total += n
            print(f"  ✅ {old} -> {new}  ({n})")

    if total:
        open(HTML, "wb").write(data.encode("utf-8"))
        print(f"\n合计 {total} 处")
    else:
        print("  （无需修复）")

    # 校验 1：$obj.纯中文属性
    g = H.unescape(data)
    bad = set()
    for m in re.finditer(r"\$(\w+)\.([\u4e00-\u9fff]+)(?=[\s\]\)\>,|&;.]|$)", g):
        bad.add(f"${m.group(1)}.{m.group(2)}")
    print(f"\n剩余 $obj.中文属性: {len(bad)}")
    for b in sorted(bad):
        print(f"  {b}")

    # 校验 2：中文数组（列出但不自动修，因为有些是自洽的）
    arrs = [m.group(1) for m in
            re.finditer(r"\[([^\[\]]{1,200})\]\s*\.\s*(?:includes|indexOf)\s*\(", g)
            if CJK.search(m.group(1))]
    print(f"\n中文数组比较（需人工判断自洽性）: {len(arrs)}")
    for a in arrs:
        print(f"  [{a}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
