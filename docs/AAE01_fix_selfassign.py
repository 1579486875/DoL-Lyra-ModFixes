"""修 var st = st 的自赋值问题。"""
import html as H
import os
import re

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(data)

print("=== 修复前 ===")
for m in re.finditer(r"var st = st;", data):
    print(f"  {data[max(0,m.start()-120):m.start()+80]!r}")

# 删掉 `var st = st;`（含前面的空白）
n1 = data.count("var st = st;")
data = data.replace("\n    var st = st;", "")
data = data.replace("var st = st;", "")
print(f"\n删掉 {n1} 处 var st = st;")

# 修正 var s = st;（这个是好的，保留）
open(HTML, "wb").write(data.encode("utf-8"))
print(f"写出 ({os.path.getsize(HTML):,} 字节)")

g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n=== 校验 ===")
print(f"  残留 var st = st: {g2.count('var st = st')}")
print(f"  残留 SugarCube.setup（非注释）: ", end="")
bad = 0
for m in re.finditer(r"SugarCube\.setup", g2):
    ctx = g2[max(0, m.start() - 60):m.start() + 60]
    if "Can be found at" in ctx:
        continue
    bad += 1
print(bad)
print(f"  新守卫: {len(re.findall(chr(39)+'typeof setup'+chr(39), g2)) + len(re.findall(chr(34)+'typeof setup'+chr(34), g2))}")

# 打印每处 <<script>> 的开头 3 行
print("\n=== 每个 <<script>> 的开头 ===")
for i, m in enumerate(re.finditer(r"<<script>>", g2), 1):
    seg = g2[m.end():m.end()+180].replace("\n", " ")
    print(f"  {i}. {seg[:150]!r}")
