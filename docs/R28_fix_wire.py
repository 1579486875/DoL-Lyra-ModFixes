"""第 28 轮：正确地把 R24 插入 build_all（用 Python 直写，避免 shell 转义）。"""
import os
import re
import sys

WORK = r"E:\TAML\_dol\work"
BA = os.path.join(WORK, "build_all.py")

s = open(BA, encoding="utf-8").read()

print("当前状态:")
print(f"  含 R24: {'R24_inject_tr' in s}")

# 先查有没有写坏的痕迹
if "R24" in s and "R24_inject_tr" not in s:
    print("  ⚠️ 有 R24 字样但不是正确路径，先清理")
    s = re.sub(r"^.*R24.*$\n?", "", s, flags=re.M)

if "R24_inject_tr" in s:
    print("  ✅ 已存在，检查位置")
else:
    # 找 ZZ01 那一行
    m = re.search(r'^([ \t]*)\(r"[^"]*ZZ01_final_guard\.py".*$', s, re.M)
    if not m:
        print("❌ 找不到 ZZ01 行")
        sys.exit(1)
    indent = m.group(1)
    # 用原始字符串构造，注意 build_all 里的路径是 E:\TAML\_dol\work\xxx.py
    new_line = (
        indent + '(r"E:\\TAML\\_dol\\work\\R24_inject_tr.py", '
        '"翻译 19 条漏翻（Asylum/Wolf Cave/Brothel 等）"),\n'
    )
    s = s[:m.start()] + new_line + s[m.start():]
    open(BA, "w", encoding="utf-8").write(s)
    print("  ✅ 已插入")

# 验证
s2 = open(BA, encoding="utf-8").read()
PAT = re.compile(r"(?:E:\\TAML\\_dol\\work\\)([A-Za-z0-9_]+\.py)")
steps = PAT.findall(s2)
print(f"\n现在共 {len(steps)} 步")
for i, f in enumerate(steps, 1):
    if f.startswith(("R24", "ZZ01", "TF01", "UB01")):
        print(f"  {i:>2}. {f}")

r24 = [i for i, f in enumerate(steps, 1) if f.startswith("R24")]
zz = [i for i, f in enumerate(steps, 1) if f.startswith("ZZ01")]
tf = [i for i, f in enumerate(steps, 1) if f.startswith("TF01")]
ub = [i for i, f in enumerate(steps, 1) if f.startswith("UB01")]

print()
ok = True
if not r24:
    print("❌ R24 仍未插入")
    ok = False
else:
    print(f"✅ R24 在第 {r24[0]} 步")
    if ub and r24[0] < ub[0]:
        print(f"❌ R24 在 UB01({ub[0]}) 之前，会被覆盖")
        ok = False
    else:
        print(f"✅ R24 在 UB01({ub[0]}) 之后")
    if zz and r24[0] < zz[0]:
        print(f"✅ R24 在 ZZ01({zz[0]}) 之前")
    else:
        print("⚠️ R24 在 ZZ01 之后（守卫不会兜底它，但 R24 本身幂等）")

sys.exit(0 if ok else 1)
