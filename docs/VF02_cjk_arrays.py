"""修所有「中文数组字面量参与代码比较」的地方。

典型：
  ["下雨", "下雪"].includes(Weather.precipitation)   <- 永远 false
  ["snow", "rain"].includes(...)                    <- 正常
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
CJK = re.compile(r"[\u4e00-\u9fff]")


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    g = H.unescape(data)

    print("=" * 94)
    print("1) 所有含中文的数组字面量（后接 .includes / .indexOf）")
    print("=" * 94)
    hits = []
    for m in re.finditer(r"\[([^\[\]]{1,200})\]\s*\.\s*(includes|indexOf)\s*\(([^)]{1,80})\)", g):
        arr, method, target = m.group(1), m.group(2), m.group(3)
        if CJK.search(arr):
            hits.append((arr, method, target, m.start()))
            print(f"\n  [{arr}]")
            print(f"    .{method}({target})")
            print(f"    @{m.start()}")

    print(f"\n共 {len(hits)} 处")

    # 已知的 Weather 修复
    print("\n" + "=" * 94)
    print("2) 修复 Weather 数组")
    print("=" * 94)
    total = 0
    FIXES = [
        ('["下雨", "下雪"]', '["rain", "snow"]'),
        ('["下雪", "下雨"]', '["snow", "rain"]'),
        ('["下雨","下雪"]', '["rain","snow"]'),
        ('["下雪","下雨"]', '["snow","rain"]'),
    ]
    for old, new in FIXES:
        for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
            if a in data:
                n = data.count(a)
                data = data.replace(a, b)
                total += n
                print(f"  ✅ {old} -> {new}  ({n} 处)")
                break

    # 检查还有没有其他中文数组
    g2 = H.unescape(data)
    remain = [m.group(1) for m in
              re.finditer(r"\[([^\[\]]{1,200})\]\s*\.\s*(?:includes|indexOf)\s*\(", g2)
              if CJK.search(m.group(1))]
    print(f"\n剩余中文数组比较: {len(remain)}")
    for r in remain[:10]:
        print(f"  [{r}]")

    if total:
        open(HTML, "wb").write(data.encode("utf-8"))
        print(f"\n合计 {total} 处，写出 {HTML}")
    else:
        print("\n（无改动）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
