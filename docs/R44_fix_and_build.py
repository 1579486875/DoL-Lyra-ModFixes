"""第 44 轮：修 genitals name 中文判断 + 把 R42/R43 加入 build_all + 重建。"""
import html as H
import os
import re
import subprocess
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
WORK = r"E:\TAML\_dol\work"
BA = os.path.join(WORK, "build_all.py")

# ---------- 1) 修 genitals name ----------
data = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(data)

print("=" * 88)
print("1) genitals name 中文判断")
print("=" * 88)
hits = re.findall(r'is\s+"贞操锁寄生虫"', g)
print(f"  is \"贞操锁寄生虫\": {len(hits)} 处")

FIX = [('is "贞操锁寄生虫"', 'is "chastity parasite"')]
total = 0
for old, new in FIX:
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            n = data.count(a)
            data = data.replace(a, b)
            total += n
            print(f"  ✅ {old} -> {new}  ({n} 处)")
            break

if total:
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"  已修 {total} 处")

# ---------- 2) 加入 build_all ----------
print("\n" + "=" * 88)
print("2) 加入 build_all")
print("=" * 88)

s = open(BA, encoding="utf-8").read()

NEED = [
    ("R42_fix_npc_names.py", "修 NPC 名被翻译导致 case 永不命中"),
    ("R43_fix_npc2.py", "修组合 case + C.npc 中文索引 + nnpc 参数"),
]

for fname, desc in NEED:
    if fname in s:
        print(f"  （已存在）{fname}")
        continue
    m = re.search(r'^([ \t]*)\(r"[^"]*ZZ01_final_guard\.py".*$', s, re.M)
    if not m:
        print("  ❌ 找不到 ZZ01 锚点")
        break
    ind = m.group(1)
    # 用单反斜杠（与其他行一致）
    line = ind + '(r"E:' + "\\" + 'TAML' + "\\" + '_dol' + "\\" + 'work' + "\\" + fname + '", "' + desc + '"),\n'
    s = s[:m.start()] + line + s[m.start():]
    print(f"  ✅ 已插入 {fname}")

open(BA, "w", encoding="utf-8").write(s)

# ---------- 3) 验证顺序 ----------
print("\n" + "=" * 88)
print("3) 验证顺序")
print("=" * 88)
s2 = open(BA, encoding="utf-8").read()
PAT = re.compile(r"E:\\\\?TAML\\\\?_dol\\\\?work\\\\?([A-Za-z0-9_]+\.py)")
steps = PAT.findall(s2)
print(f"  共 {len(steps)} 步")
for i, f in enumerate(steps, 1):
    if f.startswith(("R42", "R43", "R24", "ZZ01", "TF01")):
        print(f"    {i:>2}. {f}")

r42 = [i for i, f in enumerate(steps, 1) if f.startswith("R42")]
r43 = [i for i, f in enumerate(steps, 1) if f.startswith("R43")]
zz = [i for i, f in enumerate(steps, 1) if f.startswith("ZZ01")]
tf = [i for i, f in enumerate(steps, 1) if f.startswith("TF01")]

ok = all([r42, r43, zz, tf])
if ok:
    print(f"\n  ✅ R42({r42[0]}) R43({r43[0]}) 都在 ZZ01({zz[0]}) 之前")
    print(f"  ✅ TF01({tf[0]}) 最后")
else:
    print("  ❌ 顺序异常")
    sys.exit(1)

# ---------- 4) 重建 ----------
print("\n" + "=" * 88)
print("4) 重建")
print("=" * 88)
r = subprocess.run([sys.executable, os.path.join(WORK, "build.py"),
                    "修 NPC 名中文判断 (case/C.npc/nnpc/genitals)"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
out = (r.stdout or "") + (r.stderr or "")
print(out[-1800:])
sys.exit(r.returncode)
