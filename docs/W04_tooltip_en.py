"""W04：新维度 —— tooltip 里的英文（<mouse> / <span class="tooltip">）。

这类文本只在鼠标悬停时显示，之前的扫描（<<print>> / <<link>> / <<if>> 分支）都覆盖不到。
"""
import html as H
import json
import re
from collections import Counter

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

print("=" * 95)
print("1. <mouse> 标签里的英文")
print("=" * 95)
n1 = 0
hits1 = []
for m in re.finditer(r'<mouse[^>]*>(.*?)</mouse>', g, re.S):
    body = re.sub(r"<[^>]+>", " ", m.group(1))
    body = re.sub(r"<<[^>]*>>", " ", body)
    if re.search(r"[\u4e00-\u9fff]", body):
        # 中英混杂
        en_words = re.findall(r"\b[A-Za-z]{3,}\b", body)
        if len(en_words) >= 3:
            n1 += 1
            if len(hits1) < 20:
                hits1.append(body.strip()[:200])
    else:
        # 纯英文
        en_words = re.findall(r"\b[A-Za-z]{3,}\b", body)
        if len(en_words) >= 3:
            n1 += 1
            if len(hits1) < 20:
                hits1.append("[纯英文] " + body.strip()[:200])

print(f"  共 {n1} 处")
for h in hits1[:20]:
    print(f"    {h!r}")

print("\n" + "=" * 95)
print("2. class 含 tooltip 的元素里的英文")
print("=" * 95)
n2 = 0
hits2 = []
for m in re.finditer(r'<(?:span|div|mouse)[^>]*class="[^"]*tooltip[^"]*"[^>]*>(.*?)</(?:span|div|mouse)>', g, re.S):
    body = re.sub(r"<[^>]+>", " ", m.group(1))
    body = re.sub(r"<<[^>]*>>", " ", body)
    en_words = re.findall(r"\b[A-Za-z]{3,}\b", body)
    if len(en_words) >= 4:
        n2 += 1
        if len(hits2) < 20:
            hits2.append(body.strip()[:220])

print(f"  共 {n2} 处")
for h in hits2[:20]:
    print(f"    {h!r}")

print("\n" + "=" * 95)
print("3. title= 属性里的英文（悬停提示）")
print("=" * 95)
n3 = 0
for m in re.finditer(r'title="([^"]{6,200})"', g):
    v = m.group(1)
    if re.search(r"[\u4e00-\u9fff]", v):
        continue
    if len(re.findall(r"[A-Za-z]{3,}", v)) >= 3:
        n3 += 1
        if n3 <= 15:
            print(f"    {v!r}")
print(f"  共 {n3} 处")

print("\n" + "=" * 95)
print("汇总")
print("=" * 95)
print(f"  <mouse>:        {n1}")
print(f"  tooltip class:  {n2}")
print(f"  title 属性:     {n3}")

with open(r"E:\TAML\_dol\work\_tooltip_en.json", "w", encoding="utf-8") as f:
    json.dump({"mouse": hits1, "tooltip": hits2}, f, ensure_ascii=False, indent=1)
print("已保存 _tooltip_en.json")
