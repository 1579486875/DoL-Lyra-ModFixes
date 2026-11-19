"""修 ["Sydney", "黑狼", "Ivory Wraith"] -> Black Wolf，并确认 Weather 数组状态。"""
import html as H
import os
import re

HTML = r"E:\TAML\_dol\work\index_modded6.html"

data = open(HTML, "rb").read().decode("utf-8", "replace")

print("=" * 94)
print("1) 逐一检查 6 处中文数组在【index】里的状态")
print("=" * 94)
CHECKS = [
    '["Sydney", "黑狼", "Ivory Wraith"]',
    '["下雨", "下雪"]',
    '["男孩","女孩"]',
    '["男孩","女孩","亲爱的","挚爱","最爱"]',
    '["亲爱的","挚爱","最爱"]',
    '["登山客","混蛋"]',
]
for c in CHECKS:
    print(f"  {c:<52} {data.count(c)} 处")

print("\n" + "=" * 94)
print("2) 修复黑狼")
print("=" * 94)
total = 0
FIX = ('["Sydney", "黑狼", "Ivory Wraith"]', '["Sydney", "Black Wolf", "Ivory Wraith"]')
n = data.count(FIX[0])
if n:
    data = data.replace(FIX[0], FIX[1])
    total += n
    print(f"  ✅ {FIX[0]} -> {FIX[1]}  ({n} 处)")
else:
    print("  （未找到，可能格式不同）")
    for m in re.finditer(r"黑狼", data):
        ctx = data[max(0, m.start() - 120):m.start() + 120]
        if "includes" in ctx or "[" in ctx[:60]:
            print(f"    @{m.start()}: {ctx!r}")
            break

print("\n" + "=" * 94)
print("3) Weather 数组（在 index 里的所有形态）")
print("=" * 94)
for pat in ['下雨', '下雪']:
    for m in re.finditer(pat, data):
        ctx = data[max(0, m.start() - 60):m.start() + 60]
        if "[" in ctx and "includes" in data[m.start():m.start() + 200]:
            print(f"  @{m.start()}: {ctx!r}")
            # 修复
            seg = data[max(0, m.start() - 10):m.start() + 60]
            print(f"    片段: {seg!r}")
            break

if total:
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"\n合计 {total} 处，写出 {HTML}")

# 校验
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n=== 校验 ===")
print(f"  Black Wolf 数组: {g.count('[\"Sydney\", \"Black Wolf\", \"Ivory Wraith\"]')}")
print(f"  黑狼数组残留:   {g.count('[\"Sydney\", \"黑狼\", \"Ivory Wraith\"]')}")
