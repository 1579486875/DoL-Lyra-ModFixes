"""T13：精确扫 link/button 的英文文本（排除变量/函数表达式）。

上一版误报很多，因为把 `$worn.upper.cn_name_cap`、`setup.NPC_CN_NAME(...)` 也当文本了。
本版判据：
  1. 文本里不能含 $ / ` / ( ) [ ] => 等代码符号
  2. 必须有 3+ 个 ≥2 字母的英文词
  3. 不含中文
"""
import html as H
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))


def is_text(s):
    s = s.strip()
    if not s:
        return False
    if re.search(r"[\u4e00-\u9fff]", s):
        return False
    # 排除代码痕迹
    if re.search(r"[$`(){}\[\]]|=>|::|\.\w+\.|setup\.|\bvar\b|\bfunction\b|\breturn\b|\bnull\b|\bundefined\b", s):
        return False
    # 至少 3 个 2+ 字母的英文词
    if len(re.findall(r"[A-Za-z]{2,}", s)) < 3:
        return False
    # 不能是纯标识符/属性链
    if re.fullmatch(r"[A-Za-z0-9_.\-\s]+", s) and " " not in s:
        return False
    return True


print("=" * 95)
print("1. <<link [[文本|目标]]>> 里的英文")
print("=" * 95)
n1 = 0
for m in re.finditer(r'<<link\s+\[\[\s*([^\]|]{3,200}?)\s*\|', g):
    s = m.group(1)
    if is_text(s):
        n1 += 1
        if n1 <= 25:
            print(f"  {s!r}")
print(f"  共 {n1}")

print("\n" + "=" * 95)
print("2. <<link \"文本\">> 里的英文")
print("=" * 95)
n2 = 0
for m in re.finditer(r'<<link\s+"([^"]{3,200})"', g):
    s = m.group(1)
    if is_text(s):
        n2 += 1
        if n2 <= 25:
            print(f"  {s!r}")
print(f"  共 {n2}")

print("\n" + "=" * 95)
print("3. <<button \"文本\">> 里的英文")
print("=" * 95)
n3 = 0
for m in re.finditer(r'<<button\s+"([^"]{3,200})"', g):
    s = m.group(1)
    if is_text(s):
        n3 += 1
        if n3 <= 25:
            print(f"  {s!r}")
print(f"  共 {n3}")

print("\n" + "=" * 95)
print("4. <<option>> / <<checkbox>> / <<radiobutton>> 文本")
print("=" * 95)
n4 = 0
for m in re.finditer(r'<<(option|checkbox|radiobutton)\s+"([^"]{3,200})"', g):
    s = m.group(2)
    if is_text(s):
        n4 += 1
        if n4 <= 25:
            print(f"  [{m.group(1)}] {s!r}")
print(f"  共 {n4}")

print("\n" + "=" * 95)
print("汇总")
print("=" * 95)
print(f"  link[[...|..]]: {n1}")
print(f'  link"...":      {n2}')
print(f'  button:         {n3}')
print(f"  option 类:      {n4}")
print(f"  合计:           {n1 + n2 + n3 + n4}")
