"""V03：扫 _text_output 拼接 + widget 顶层裸英文。

两个高价值维度：
  1. <<set _text_output += "英文">> 或 _text_output 直接拼英文
  2. widget 里不在任何分支、直接输出的英文段落
"""
import html as H
import re
from collections import Counter

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

PASSAGES = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', g, re.S):
    PASSAGES[m.group(1)] = m.group(2)


def clean_en(s, minw=2):
    s = s.strip()
    if not s or re.search(r"[\u4e00-\u9fff]", s):
        return False
    if s.startswith("<") or re.search(r"[${}()\[\];=<>`]", s):
        return False
    if len(re.findall(r"[A-Za-z]{2,}", s)) < minw:
        return False
    return True


print("=" * 95)
print("1. _text_output 拼接英文")
print("=" * 95)
n1 = 0
hits1 = []
# 形态 A: += "英文"
for m in re.finditer(r'_text_output\s*\+=\s*"([^"]{3,120})"', g):
    if clean_en(m.group(1), 1):
        n1 += 1
        hits1.append(m.group(1))
print(f"  _text_output += \"英文\": {n1}")
for h in hits1[:15]:
    print(f"    {h!r}")

# 形态 B: <<set _text_output to "英文">>
n1b = 0
for m in re.finditer(r'<<set\s+_text_output\s+to\s+"([^"]{3,120})"', g):
    if clean_en(m.group(1), 1):
        n1b += 1
        if n1b <= 15:
            print(f"    [to] {m.group(1)!r}")
print(f"  <<set _text_output to \"英文\">>: {n1b}")

print("\n" + "=" * 95)
print("2. widget 里「不在任何分支」的裸英文行")
print("=" * 95)
n2 = 0
samples2 = []
for pname, body in PASSAGES.items():
    for wm in re.finditer(r'<<widget\s+"([^"]+)"[^>]*>>(.*?)<</widget>>', body, re.S):
        wname = wm.group(1)
        wbody = wm.group(2)
        # 逐行看：不在 << >> 里的纯文本行
        depth = 0
        for ln in wbody.split("\n"):
            stripped = ln.strip()
            if not stripped:
                continue
            # 统计这一行的宏嵌套深度变化
            opens = len(re.findall(r"<<(?![/])", ln))
            closes = len(re.findall(r"<</", ln))
            at_top = (depth == 0)
            depth += opens - closes
            if depth < 0:
                depth = 0
            if not at_top:
                continue
            if stripped.startswith("<") or stripped.startswith("|"):
                continue
            if clean_en(stripped, 2) and len(stripped) > 6:
                n2 += 1
                if len(samples2) < 25:
                    samples2.append((wname, stripped[:100]))
print(f"  共 {n2} 处")
seen = set()
for w, s in samples2:
    if s in seen:
        continue
    seen.add(s)
    print(f"    [{w}] {s!r}")

print("\n" + "=" * 95)
print("3. <<= >> 表达式输出英文字符串字面量")
print("=" * 95)
n3 = 0
for m in re.finditer(r'<<=\s*"([^"]{3,120})"\s*>>', g):
    if clean_en(m.group(1), 1):
        n3 += 1
        if n3 <= 15:
            print(f"    {m.group(1)!r}")
print(f"  共 {n3} 处")

print("\n" + "=" * 95)
print("4. <<print>> 短英文（1-2 词）")
print("=" * 95)
n4 = 0
for m in re.finditer(r'<<print\s+"([^"]{2,60})"', g):
    v = m.group(1)
    if clean_en(v, 1) and len(v) < 40:
        n4 += 1
        if n4 <= 20:
            print(f"    {v!r}")
print(f"  共 {n4} 处")

print("\n" + "=" * 95)
print("汇总")
print("=" * 95)
print(f"  _text_output += 英文: {n1}")
print(f"  _text_output to 英文: {n1b}")
print(f"  widget 顶层裸英文:    {n2}")
print(f"  equal-print 英文:     {n3}")
print(f"  <<print 短英文:       {n4}")
