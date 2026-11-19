import html
import re

g = html.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

names = re.findall(r'<<widget\s+["\']([^"\']+)["\']', g)
print(f"widget 总数: {len(names)}")

bad = [n for n in names if re.search(r"[^\x00-\x7f]", n)]
print(f"含非 ASCII 的 widget 名: {len(bad)}")
for n in bad[:15]:
    print("  ", repr(n))

print()
# 已知的两个坏名
for probe in ("characteristics", "flesh_text"):
    hit = [n for n in names if probe in n]
    print(f"  含 {probe!r} 的: {hit}")

# 检查是否有 'ch一↑' 这种
broken = [n for n in names if re.search(r"[\u4e00-\u9fff\u2191]", n)]
print(f"\n名字里含中文或箭头符号的: {len(broken)}")
for n in broken[:10]:
    print("  ", repr(n))
