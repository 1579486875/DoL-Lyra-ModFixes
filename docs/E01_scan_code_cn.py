"""E01（第1轮）：系统性扫描「中文被插入代码位置」。

上轮发现 `<<if>>` 里 && 被翻成「且」是致命的。
同类还可能：
  1. 运算符：&& || >= <= == != + - * /
  2. SugarCube 关键字：is isnot gte lte gt lt to and or not true false undefined
  3. 变量名：$xxx / _xxx
  4. 宏名：<<xxx>>
  5. 属性名：.xxx
  6. 函数名：Math.xxx / setup.xxx / State.xxx / V.xxx

判据：在代码位置（宏内部、$/_ 变量后、点号后）出现中文字符。
"""
import html
import json
import re
import zipfile
from collections import Counter

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
g = html.unescape(zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace"))
CJK = "[\u4e00-\u9fff]"

# SugarCube 关键字（如果被翻译，代码必坏）
KEYWORDS = ["is", "isnot", "gte", "lte", "gt", "lt", "to", "and", "or", "not",
            "true", "false", "undefined", "null", "def", "temp", "eq", "neq",
            "includes", "contains", "startsWith", "endsWith", "typeof"]

# 中文里等价的词（被误翻的信号）
CN_OPS = ["且", "并且", "而且", "或", "或者", "不是", "等于", "大于", "小于",
          "大于等于", "小于等于", "不等于", "真", "假", "未定义", "空"]

results = {}

def add(cat, text, pos, ctx):
    results.setdefault(cat, []).append({"text": text, "pos": pos, "ctx": ctx[:220]})


print("=" * 100)
print("1) 宏内部的中文运算符（<<if>>/<<elseif>>/<<set>>/<<run>> 等）")
print("=" * 100)
for m in re.finditer(r"<<(if|elseif|set|run|switch|case|for|while|until)\b([^<>]{0,600}?)>>", g):
    body = m.group(2)
    if not re.search(CJK, body):
        continue
    # 排除中文在字符串里的正常情况
    # 把 "..." 和 '...' 和 `...` 里的内容挖掉
    stripped = re.sub(r'"[^"]*"|\'[^\']*\'|`[^`]*`', '""', body)
    if not re.search(CJK, stripped):
        continue
    # 剩下还有中文 = 代码位置
    cn_ops = [w for w in CN_OPS if w in stripped]
    add("宏内中文运算符", m.group(0)[:200], m.start(),
        (f"CN_OPS={cn_ops} " if cn_ops else "") + stripped[:180])

print(f"  命中 {len(results.get('宏内中文运算符', []))}")

print("\n" + "=" * 100)
print("2) 变量名/属性名里的中文")
print("=" * 100)
for m in re.finditer(r"[$_][A-Za-z0-9_]*" + CJK + r"[A-Za-z0-9_]*", g):
    add("变量名含中文", m.group(0), m.start(), g[max(0, m.start() - 100):m.start() + 100])
for m in re.finditer(r"\." + CJK + r"[A-Za-z0-9_]*", g):
    add("属性名含中文", m.group(0), m.start(), g[max(0, m.start() - 100):m.start() + 100])

print(f"  变量名: {len(results.get('变量名含中文', []))}")
print(f"  属性名: {len(results.get('属性名含中文', []))}")

print("\n" + "=" * 100)
print("3) 宏名里的中文")
print("=" * 100)
for m in re.finditer(r"<<\s*/?\s*" + CJK + r"[^<>]{0,40}>>", g):
    add("宏名含中文", m.group(0), m.start(), g[max(0, m.start() - 100):m.start() + 100])

print(f"  宏名: {len(results.get('宏名含中文', []))}")

print("\n" + "=" * 100)
print("4) 中文被插在英文单词中间（如 深色ness）")
print("=" * 100)
for m in re.finditer(CJK + r"+[a-z]{2,}", g):
    t = m.group(0)
    # 排除正常中文后面跟英文缩写
    if len(t) > 20:
        continue
    add("中英粘连", t, m.start(), g[max(0, m.start() - 80):m.start() + 80])
for m in re.finditer(r"[A-Za-z]{2,}" + CJK + r"+", g):
    t = m.group(0)
    if len(t) > 20:
        continue
    add("英中粘连", t, m.start(), g[max(0, m.start() - 80):m.start() + 80])

print(f"  中英粘连: {len(results.get('中英粘连', []))}")
print(f"  英中粘连: {len(results.get('英中粘连', []))}")

print("\n" + "=" * 100)
print("汇总")
print("=" * 100)
for cat, items in results.items():
    print(f"\n### {cat}  ({len(items)} 处)")
    seen = Counter()
    for it in items:
        seen[it["text"]] += 1
    for t, c in seen.most_common(25):
        print(f"  {c:>3}x {t!r}")

with open(r"E:\TAML\_dol\work\_code_cn_scan.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print(f"\n已保存 _code_cn_scan.json")
