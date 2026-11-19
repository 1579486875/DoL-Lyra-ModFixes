"""A21：找 Curvy女人 的运行时拼接点。"""
import re
import zipfile

g = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk").read(
    "assets/www/index.html").decode("utf-8", "replace")

print("=" * 90)
print("1) 显示上下文的 bodyshape 用法")
print("=" * 90)
n = 0
for m in re.finditer(r"(?:\$|\.)bodyshape\b", g):
    ctx = g[max(0, m.start() - 160):m.start() + 160]
    if any(k in ctx for k in ("<<=", "${", "<<print", "capitalise", "ucfirst", "toUpperFirst")):
        n += 1
        print(f"\n  @{m.start()}: {ctx!r}")
        if n >= 8:
            break
print(f"  共 {n} 处带显示特征")

print("\n" + "=" * 90)
print("2) NPC bodyshape 的数据表")
print("=" * 90)
for m in re.finditer(r"bodyshape\s*[:=]\s*\[", g):
    print(f"  {g[m.start():m.start()+450]!r}\n")

print("\n" + "=" * 90)
print("3) 找 bodyShape 的所有中文映射")
print("=" * 90)
for m in re.finditer(r"textMap:\s*\{[^}]*curvy[^}]*\}", g):
    print(f"  {m.group(0)!r}")

print("\n" + "=" * 90)
print("4) 找 bodyShapeOptions / npcBodyShape")
print("=" * 90)
for kw in ("bodyShapeOptions", "npcBodyShape", "bodyShapes", "bodyshapes"):
    for m in list(re.finditer(kw, g))[:2]:
        print(f"  [{kw}] {g[max(0,m.start()-80):m.start()+250]!r}\n")

print("=" * 90)
print("5) 找含 'curvy' 的数组（可能是 NPC 身形词表）")
print("=" * 90)
for m in re.finditer(r"\[[^\[\]]{0,400}\"curvy\"[^\[\]]{0,400}\]", g):
    s = m.group(0)
    if len(s) < 500:
        print(f"  {s[:400]!r}\n")
