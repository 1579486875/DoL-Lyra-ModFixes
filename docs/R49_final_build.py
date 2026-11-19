"""第 49 轮：把 R46 加入 build_all 并重建。"""
import os
import re
import subprocess
import sys

WORK = r"E:\TAML\_dol\work"
BA = os.path.join(WORK, "build_all.py")

s = open(BA, encoding="utf-8").read()

if "R46_fix_yourself" in s:
    print("（已存在）")
else:
    m = re.search(r'^([ \t]*)\(r"[^"]*ZZ01_final_guard\.py".*$', s, re.M)
    if not m:
        print("❌ 找不到 ZZ01")
        sys.exit(1)
    ind = m.group(1)
    line = ind + '(r"E:' + "\\" + 'TAML' + "\\" + '_dol' + "\\" + 'work' + "\\" + 'R46_fix_yourself.py", "修 === \u4f60\u81ea\u5df1 -> Yourself"),\n'
    s = s[:m.start()] + line + s[m.start():]
    open(BA, "w", encoding="utf-8").write(s)
    print("✅ 已插入 R46")

# 验证
s2 = open(BA, encoding="utf-8").read()
PAT = re.compile(r"E:\\\\?TAML\\\\?_dol\\\\?work\\\\?([A-Za-z0-9_]+\.py)")
steps = PAT.findall(s2)
print(f"\n共 {len(steps)} 步")
for i, f in enumerate(steps, 1):
    if f.startswith(("R42", "R43", "R46", "R24", "ZZ01", "TF01")):
        print(f"  {i:>2}. {f}")

r46 = [i for i, f in enumerate(steps, 1) if f.startswith("R46")]
zz = [i for i, f in enumerate(steps, 1) if f.startswith("ZZ01")]
tf = [i for i, f in enumerate(steps, 1) if f.startswith("TF01")]
if not (r46 and zz and tf and r46[0] < zz[0] and tf[0] == len(steps)):
    print("❌ 顺序异常")
    sys.exit(1)
print(f"\n✅ R46({r46[0]}) < ZZ01({zz[0]}) < TF01({tf[0]}=最后)")

print("\n开始重建 ...")
r = subprocess.run([sys.executable, os.path.join(WORK, "build.py"),
                    "修 Yourself 判断 + 最终守卫 + NPC 名"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
print(((r.stdout or "") + (r.stderr or ""))[-1600:])
sys.exit(r.returncode)
