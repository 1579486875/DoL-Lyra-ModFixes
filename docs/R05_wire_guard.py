"""第 5 轮：把 ZZ01_final_guard 插到 TF01 之前。"""
import os
import re

WORK = r"E:\TAML\_dol\work"
BA = os.path.join(WORK, "build_all.py")

s = open(BA, encoding="utf-8").read()

if "ZZ01_final_guard" in s:
    print("（已存在，检查位置）")
    i_zz = s.find("ZZ01_final_guard")
    i_tf = s.find("TF01_nest_guard")
    print(f"  ZZ01 位置 {i_zz}  TF01 位置 {i_tf}  {'✅ 在之前' if i_zz < i_tf else '❌ 在之后'}")
else:
    # TF01 那一行
    m = re.search(r'^(\s*)\(r"[^"]*TF01_nest_guard\.py".*$', s, re.M)
    if not m:
        print("❌ 找不到 TF01 行")
        raise SystemExit(1)
    indent = m.group(1)
    new_line = (
        f'{indent}(r"E:\\TAML\\_dol\\work\\ZZ01_final_guard.py", '
        f'"最终守卫：所有已知 bug 的幂等兜底（防顺序错）"),\n'
    )
    s = s[:m.start()] + new_line + s[m.start():]
    open(BA, "w", encoding="utf-8").write(s)
    print("✅ 已插入 ZZ01 到 TF01 之前")

# 验证
s2 = open(BA, encoding="utf-8").read()
PAT = re.compile(r"(?:E:\\TAML\\_dol\\work\\)([A-Za-z0-9_]+\.py)")
steps = PAT.findall(s2)
print(f"\n现在共 {len(steps)} 步")
for i, f in enumerate(steps[-4:], len(steps) - 3):
    print(f"  {i}. {f}")

# 纪律检查
tf = [i for i, f in enumerate(steps, 1) if f.startswith("TF01")]
zz = [i for i, f in enumerate(steps, 1) if f.startswith("ZZ01")]
print(f"\n  TF01: {tf}  ZZ01: {zz}")
if tf and zz and zz[0] < tf[0] and tf[0] == len(steps):
    print("  ✅ ZZ01 在 TF01 之前，TF01 仍是最后一步")
else:
    print("  ❌ 顺序不对")
