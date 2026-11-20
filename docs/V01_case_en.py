"""V01（第4轮）：扫 <<switch>>/<<case>> 分支里的裸英文（与 <<if>> 同类）。

形态：
  <<switch $x>>
    <<case "a">>
      english_word          ← 这类
    <<case "b">>
      中文
  <</switch>>
"""
import html as H
import json
import re
from collections import Counter

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))


def is_word(s):
    s = s.strip()
    if not s or len(s) < 2 or len(s) > 45:
        return False
    if re.search(r"[\u4e00-\u9fff]", s):
        return False
    if s.startswith("<") or re.search(r"[${}()\[\];=<>]", s):
        return False
    if re.search(r"[\u4e00-\u9fff]", s):
        return False
    return bool(re.match(r"^[A-Za-z][A-Za-z\- ']*$", s))


# ---- 1. <<case>> 分支 ----
PAT_CASE = re.compile(r"<<case\b[^>]*>>\s*\n\s*([^\n<]{1,50})\s*\n\s*<<", re.M)
hits_case = []
for m in PAT_CASE.finditer(g):
    w = m.group(1).strip()
    if is_word(w):
        hits_case.append((m.start(), w, g[max(0, m.start() - 120):m.start() + 180]))

print("=" * 95)
print(f"1. <<case>> 分支里的裸英文：{len(hits_case)} 处")
print("=" * 95)
cnt = Counter(h[1] for h in hits_case)
for w, c in cnt.most_common(40):
    print(f"  {c:>3}  {w!r}")
print()
for pos, w, ctx in hits_case[:20]:
    print(f"  @{pos}  [{w}]")
    print(f"    {ctx!r}")

# ---- 2. <<default>> 分支 ----
print("\n" + "=" * 95)
print("2. <<default>> 分支")
print("=" * 95)
PAT_DEF = re.compile(r"<<default\b[^>]*>>\s*\n\s*([^\n<]{1,50})\s*\n\s*<<", re.M)
n2 = 0
for m in PAT_DEF.finditer(g):
    w = m.group(1).strip()
    if is_word(w):
        n2 += 1
        if n2 <= 10:
            print(f"  @{m.start()}  {w!r}")
            print(f"    {g[max(0,m.start()-120):m.start()+180]!r}")
print(f"  共 {n2} 处")

# ---- 3. <<for>> 循环体 ----
print("\n" + "=" * 95)
print("3. <<for>> 循环体里的裸英文")
print("=" * 95)
PAT_FOR = re.compile(r"<<for\b[^>]*>>\s*\n\s*([^\n<]{1,50})\s*\n\s*<<", re.M)
n3 = 0
for m in PAT_FOR.finditer(g):
    w = m.group(1).strip()
    if is_word(w):
        n3 += 1
        if n3 <= 10:
            print(f"  @{m.start()}  {w!r}")

print(f"  共 {n3} 处")

# ---- 4. 中文里夹的孤立英文单词（left手 那类）----
print("\n" + "=" * 95)
print("4. 中文里夹的孤立英文单词")
print("=" * 95)
n4 = 0
samples = []
for m in re.finditer(r"[\u4e00-\u9fff]{1,6}([A-Za-z]{2,12})[\u4e00-\u9fff]{1,6}", g):
    w = m.group(1)
    # 排除技术词与已知缩写
    if w.lower() in ("html", "css", "js", "png", "jpg", "id", "url", "api",
                     "xp", "hp", "npc", "pc", "rng", "ok", "ui", "lewd",
                     "and", "the", "of", "to", "is", "a", "an"):
        continue
    n4 += 1
    if len(samples) < 25:
        samples.append((m.start(), w, g[max(0, m.start() - 40):m.start() + 60]))
print(f"  共 {n4} 处（去重看下面）")
cc = Counter(s[1] for s in samples)
for w, c in cc.most_common(25):
    print(f"  {w!r}")

with open(r"E:\TAML\_dol\work\_bare_case_en.json", "w", encoding="utf-8") as f:
    json.dump({"case": hits_case[:100]}, f, ensure_ascii=False, indent=1)
print(f"\n已保存 _bare_case_en.json")
