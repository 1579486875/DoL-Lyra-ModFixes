"""E27：从基线恢复 + 安全补 Widgets Repair（不用字符串拼接）。"""
import html as H
import os
import re
import subprocess
import sys
import zipfile

WORK = r"E:\TAML\_dol\work"
HTML = os.path.join(WORK, "index_modded6.html")
ARCHIVE = r"E:\TAML\_dol\archive"
GOOD = os.path.join(ARCHIVE, "DoL-Lyra-0.5.12.13-CHS-modded_20261120-061313_修复arsc可安装.apk")

# 1) 恢复基线
z = zipfile.ZipFile(GOOD)
base = z.read("assets/www/index.html").decode("utf-8", "replace")
z.close()
open(HTML, "wb").write(base.encode("utf-8"))
n = len(re.findall(r"<tw-passagedata[^>]*name=", base))
print(f"✅ 恢复基线: passage {n}, {len(base)/1048576:.2f} MB")

# 2) 跑 D01 -> E02 -> E17（不跑 E24）
print("\n" + "=" * 90)
print("修复链 D01 -> E02 -> E17")
print("=" * 90)
for s in ("D01_fix_all_escaped.py", "E02_fix_identifiers.py", "E17_fix_npctypelist.py"):
    p = os.path.join(WORK, s)
    r = subprocess.run([sys.executable, p], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    out = ((r.stdout or "") + (r.stderr or "")).strip().split("\n")
    print(f"\n[{s}] exit={r.returncode}")
    for line in out[-3:]:
        print(f"    {line}")

# 3) 校验（E17 之后 Widgets Repair 应该还在）
data = open(HTML, "rb").read().decode("utf-8", "replace")
n2 = len(re.findall(r"<tw-passagedata[^>]*name=", data))
has_wr = bool(re.search(r'<tw-passagedata[^>]*name="Widgets Repair"', data))
print(f"\n  passage: {n2}")
print(f"  Widgets Repair: {'✅ 在' if has_wr else '❌ 缺'}")

# 4) 如果缺，用「双列表拼接」安全插入（不破坏原有结构）
if not has_wr:
    print("\n  补 Widgets Repair（安全方式）...")
    good = zipfile.ZipFile(GOOD).read("assets/www/index.html").decode("utf-8", "replace")
    m = re.search(r'<tw-passagedata[^>]*name="Widgets Repair"[^>]*>.*?</tw-passagedata>', good, re.S)
    if not m:
        print("  ❌ 基线里也没有")
        sys.exit(1)
    block = m.group(0)
    # 用 re.sub 的 lambda（安全，无转义问题）
    # 找到最后一个 </tw-passagedata> 的位置
    last_close = data.rfind("</tw-passagedata>")
    if last_close < 0:
        print("  ❌ 找不到插入点")
        sys.exit(1)
    insert_at = last_close + len("</tw-passagedata>")
    # 分两段拼接
    part1 = data[:insert_at]
    part2 = data[insert_at:]
    data = part1 + "\n" + block + part2
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"  ✅ 已插入 {len(block)} 字符")

# 5) 最终校验
raw = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(raw)
print("\n" + "=" * 90)
print("最终校验")
print("=" * 90)
print(f"  passage: {len(re.findall(r'<tw-passagedata[^>]*name=', raw))}")
print(f"  大小: {len(raw)/1048576:.2f} MB")
print(f"  Widgets Repair: {len(re.findall(r'name=.Widgets Repair.', raw))}")
for kw in ("catboy,猫男", "catgirl,猫娘", "doggirl,狗娘", "curvy,曲线玲珑", "shapely,曲线优美"):
    print(f"  {'✅' if kw in g else '❌'} {kw}")
for kw in ("_下体。", "Tendrils of 深色ness", "Your eyes itch"):
    print(f"  {'✅' if kw not in g else '❌'} {kw!r} 残留")
bad = sum(1 for m in re.finditer(r"<<(if|elseif|set|run|switch|case|for|while)\b([^<>]{0,800}?)>>", g)
          if re.search(r"[\u4e00-\u9fff]", re.sub(r'"[^"]*"|\'[^\']*\'|`[^`]*`', lambda mm: " " * len(mm.group(0)), m.group(2))))
print(f"  {'✅' if bad == 0 else '❌'} 代码位置含中文: {bad}")
