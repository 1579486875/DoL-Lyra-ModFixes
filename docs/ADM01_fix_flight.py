"""修 flight_text 被翻成 flesh_text 的问题（我之前兜底脚本映射错了）。"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
QO02 = r"E:\TAML\_dol\work\QO02_widget_cleanup.py"

data = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(data)

print("=" * 80)
print("1) flesh_text 出现位置")
print("=" * 80)
n = 0
for m in re.finditer(r"flesh_text", g):
    n += 1
    if n <= 5:
        print(f"  {g[max(0,m.start()-120):m.start()+120]!r}")
print(f"  共 {n} 处")

print("\n" + "=" * 80)
print("2) vanilla 里的 flight_text")
print("=" * 80)
import zipfile
vz = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk")
vg = H.unescape(vz.read("assets/www/index.html").decode("utf-8", "replace"))
for m in list(re.finditer(r"flight_text", vg))[:5]:
    print(f"  {vg[max(0,m.start()-180):m.start()+180]!r}")

print("\n" + "=" * 80)
print("3) 修复")
print("=" * 80)
total = 0
for a, b in (("flesh_text", "flight_text"),
             (H.escape("flesh_text", quote=False), H.escape("flight_text", quote=False))):
    if a in data:
        c = data.count(a)
        data = data.replace(a, b)
        total += c
        print(f"  ✅ {a} -> {b}  ({c} 处)")
        break

if total:
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")

# 4) 修 QO02 的映射
print("\n" + "=" * 80)
print("4) 修 QO02_widget_cleanup 的映射")
print("=" * 80)
if os.path.exists(QO02):
    s = open(QO02, encoding="utf-8").read()
    if '"flesh_text": "flight_text"' not in s:
        # 替换/新增映射
        if '"f浅色_text": "flesh_text"' in s:
            s = s.replace('"f浅色_text": "flesh_text"', '"f浅色_text": "flight_text"')
            print("  ✅ 已修正 MANUAL 映射 f浅色_text -> flight_text")
        elif '"f浅色_text"' in s:
            s = re.sub(r'"f浅色_text":\s*"[^"]*"', '"f浅色_text": "flight_text"', s)
            print("  ✅ 已修正 MANUAL 映射")
        else:
            print("  ⚠️ 未找到 f浅色_text 映射")
        open(QO02, "w", encoding="utf-8").write(s)
    else:
        print("  （已正确）")

# 校验
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n=== 校验 ===")
print(f"  flight_text: {len(re.findall('flight_text', g2))}")
print(f"  flesh_text:  {len(re.findall('flesh_text', g2))}")
