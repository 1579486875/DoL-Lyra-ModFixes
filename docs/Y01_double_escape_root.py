"""Y01（第7轮）：查双重转义的根源 —— 是哪个脚本干的？

方法：
  1. 验证当前包有没有复发
  2. 在 build_all 里找会做 html.escape 的脚本
  3. 检查 X05 在构建链里的位置（之后还有没有脚本会重新转义）
"""
import html as H
import os
import re
import zipfile

WORK = r"E:\TAML\_dol\work"
APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"

print("=" * 95)
print("1. 当前包 / 工作 index 的双重转义状态")
print("=" * 95)
raw_apk = zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace")
raw_idx = open(os.path.join(WORK, "index_modded6.html"), "rb").read().decode("utf-8", "replace")

for label, t in (("APK", raw_apk), ("index", raw_idx)):
    print(f"  [{label}]  &amp;lt;={t.count('&amp;lt;')}  &amp;gt;={t.count('&amp;gt;')}  &amp;amp;={t.count('&amp;amp;')}")

print("\n" + "=" * 95)
print("2. build_all 里所有脚本，检查哪些会做 html.escape / escape(")
print("=" * 95)
BA = os.path.join(WORK, "build_all.py")
s = open(BA, encoding="utf-8").read()
PAT = re.compile(r'E:\\\\?TAML\\\\?_dol\\\\?work\\\\?([A-Za-z0-9_]+\.py)')
steps = PAT.findall(s)
print(f"  共 {len(steps)} 步")

risky = []
for i, f in enumerate(steps, 1):
    p = os.path.join(WORK, f)
    if not os.path.exists(p):
        continue
    src = open(p, encoding="utf-8", errors="replace").read()
    # 找危险的整文件 escape
    bad = []
    if re.search(r"h\.escape\(\s*data\s*[,)]", src) or re.search(r"html\.escape\(\s*data\s*[,)]", src):
        bad.append("整份 data escape ★★★")
    if re.search(r"\.escape\(\s*data\s*[,)]", src):
        bad.append("data.escape")
    if "replace(\"&amp;" in src or "replace('&amp;" in src:
        bad.append("替换 &amp;")
    if bad:
        risky.append((i, f, bad))

if risky:
    print(f"\n  危险脚本 {len(risky)} 个:")
    for i, f, bad in risky:
        print(f"    {i:>2}. {f:<40} {bad}")
else:
    print("\n  ✅ 没有脚本对整份 data 做 escape")

print("\n" + "=" * 95)
print("3. X05 在构建链里的位置")
print("=" * 95)
for i, f in enumerate(steps, 1):
    if f in ("X05_fix_leaks.py", "TF01_nest_guard.py", "ZZ01_final_guard.py",
             "inject6.py", "D01_fix_all_escaped.py"):
        mark = " ★最后" if f == "TF01_nest_guard.py" else ""
        print(f"  {i:>2}. {f}{mark}")

print("\n  X05 之后的步骤:")
found = False
for i, f in enumerate(steps, 1):
    if f == "X05_fix_leaks.py":
        found = True
        continue
    if found:
        print(f"    {i:>2}. {f}")

print("\n" + "=" * 95)
print("4. D01_fix_all_escaped.py 在干什么（名字可疑）")
print("=" * 95)
d1 = os.path.join(WORK, "D01_fix_all_escaped.py")
if os.path.exists(d1):
    src = open(d1, encoding="utf-8").read()
    print(f"  行数: {len(src.splitlines())}")
    # 打印前 40 行
    for ln in src.splitlines()[:40]:
        print(f"    {ln}")
else:
    print("  不存在")
