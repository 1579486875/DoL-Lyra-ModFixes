"""Z03：查 2 处 <<listbox>> 的上下文 + 确认 statDisplay Test 是调试用。"""
import html as H
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

print("=" * 95)
print("1. <<listbox>> VFast/Fast/Mid/Slow")
print("=" * 95)
for m in re.finditer(r"<<listbox[^>]*>>(?:.*?)(?:VFast|vfast)", g, re.S):
    print(f"  @{m.start()}")
    print(f"  {g[max(0, m.start() - 400):m.start() + 800]!r}")
    print()

print("=" * 95)
print("2. <<listbox>> regular/large/massive")
print("=" * 95)
for m in re.finditer(r"massive", g):
    ctx = g[max(0, m.start() - 500):m.start() + 300]
    if "<<listbox" in ctx or "<<option" in ctx:
        print(f"  @{m.start()}")
        print(f"  {ctx!r}")
        print()

print("=" * 95)
print("3. statDisplay Test 是什么")
print("=" * 95)
for m in list(re.finditer(r'statDisplay Test', g))[:2]:
    print(f"  @{m.start()}")
    print(f"  {g[max(0, m.start() - 300):m.start() + 300]!r}")
    print()

print("=" * 95)
print("4. 这些在不在 debug 条件里")
print("=" * 95)
# 找 VFast 附近有没有 debug 判断
i = g.find("VFast")
if i > 0:
    seg = g[max(0, i - 2000):i + 500]
    print(f"  VFast 前 2000 字里的 debug 相关:")
    for kw in ("debug", "$options.debug", "options.debugdisable"):
        n = seg.count(kw)
        if n:
            print(f"    {kw!r}: {n} 次")
