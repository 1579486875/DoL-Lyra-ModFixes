"""T04（第 2 轮深挖）：G 类英文残留 —— 扩大扫描面。

上次只扫了 <<print>> 和 <<either>>，这次补：
1. <<option>> / <<checkbox>> / <<radiobutton>> 文本
2. <<link>> 文本（3+ 词）
3. <<button>> 文本
4. Template.add 里还没翻的（对比 _template_en.json）
5. 半翻（中文里夹 3+ 连续英文词）
"""
import html as H
import json
import os
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))


def pure_en(s, minw=3):
    s = s.strip()
    if not s or re.search(r"[\u4e00-\u9fff]", s):
        return False
    if len(re.findall(r"[A-Za-z]{2,}", s)) < minw:
        return False
    if re.search(r"[{}`\\]|=>|\bfunction\b|\bvar\b|\bconst\b|\breturn\b|\bundefined\b|^[a-z_.]+$", s):
        return False
    return True


def report(title, results, limit=12):
    print("\n" + "=" * 95)
    print(title)
    print("=" * 95)
    print(f"  共 {len(results)} 处")
    for r in results[:limit]:
        print(f"    {r[:150]!r}")
    if len(results) > limit:
        print(f"    ... 还有 {len(results) - limit}")


# ---- 1. option / checkbox / radiobutton ----
r1 = []
for m in re.finditer(r'<<(option|checkbox|radiobutton)\s+"([^"]{3,150})"', g):
    if pure_en(m.group(2), 2):
        r1.append(f"[{m.group(1)}] {m.group(2)}")
report("1. <<option>>/<<checkbox>>/<<radiobutton>> 纯英文", r1)

# ---- 2. link 文本 ----
r2 = []
for m in re.finditer(r'<<link\s+\[\[\s*([^\]|]{8,150}?)\s*[|\]]', g):
    if pure_en(m.group(1), 3):
        r2.append(m.group(1))
report("2. <<link>> 纯英文（3+ 词）", r2)

# ---- 3. button 文本 ----
r3 = []
for m in re.finditer(r'<<button\s+"([^"]{8,150})"', g):
    if pure_en(m.group(1), 3):
        r3.append(m.group(1))
report("3. <<button>> 纯英文", r3)

# ---- 4. Template.add 剩余英文 ----
r4 = []
jp = r"E:\TAML\_dol\work\_template_en.json"
if os.path.exists(jp):
    old = json.load(open(jp, encoding="utf-8"))
    for name, words in old.items():
        for w in words:
            if ('"' + w + '"') in g:
                r4.append(f"?{name}: {w}")
report("4. Template.add 里仍存在的英文（对比旧快照）", r4, 20)
if not os.path.exists(jp):
    print("  （_template_en.json 不存在，跳过）")

# ---- 5. 半翻：中文里夹 3+ 连续英文词 ----
TICK = chr(96)
r5 = []
for m in re.finditer(r"[\u4e00-\u9fff][^<>\n]{0,80}", g):
    seg = m.group(0)
    for mm in re.finditer(r"\b([A-Za-z]{3,}(?:\s+[A-Za-z]{3,}){2,})\b", seg):
        w = mm.group(1)
        if re.search(r"^(?:the|and|you|her|his|with|that|this|from|into|onto)\s", w, re.I):
            continue
        r5.append(seg[max(0, mm.start() - 20):mm.start() + 60])
        break
report("5. 中文里夹 3+ 连续英文词", r5)

# ---- 6. 整句英文（句末标点 + 4+ 词）----
r6 = []
for m in re.finditer(r"[>\n]([A-Z][a-z][^<>\n]{18,120}[.!?])(?=[\s<\n])", g):
    s = m.group(1).strip()
    if re.search(r"[\u4e00-\u9fff]", s):
        continue
    if len(re.findall(r"[A-Za-z]{2,}", s)) < 4:
        continue
    r6.append(s)
report("6. 正文整句英文", r6, 20)

print("\n" + "=" * 95)
print("汇总")
print("=" * 95)
print(f"  option/checkbox: {len(r1)}")
print(f"  link:           {len(r2)}")
print(f"  button:         {len(r3)}")
print(f"  Template 残留:  {len(r4)}")
print(f"  半翻:           {len(r5)}")
print(f"  整句英文:       {len(r6)}")
