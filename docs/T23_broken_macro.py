"""T23：扫「宏名被破坏」的残留 —— 这类会在正文里原样显示给玩家。

常见形态：
  sets $x to ...     ← <<set>> 少了尖括号
  calls <<xxx>>      ← <<call>> 或 <<>> 被改
  ifs / elseifs / prints / runs
  << set ... >>      ← 空格（SugarCube 其实允许，不算错）
"""
import html as H
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

PASSAGES = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', g, re.S):
    PASSAGES[m.group(1)] = m.group(2)

# 宏名 + 多余字母
BAD_MACROS = ["sets", "ifs", "elseifs", "elses", "prints", "runs", "links",
              "buttons", "widgets", "includes", "displays", "switchs", "cases",
              "fors", "whiles", "unset s", "silentlys"]

print("=" * 95)
print("1. 宏名后多出字母（sets / ifs / prints ...）")
print("=" * 95)
total = 0
for pname, body in PASSAGES.items():
    for bm in BAD_MACROS:
        # 匹配「bm + 空格 + $/_」或「bm + 空格 + <<」
        for m in re.finditer(r"(?<![A-Za-z<])" + re.escape(bm) + r"\s+(?=[$_<])", body):
            total += 1
            if total <= 20:
                print(f"  [{pname}] @{m.start()}: {body[max(0,m.start()-60):m.start()+120]!r}")
print(f"  共 {total} 处")

print("\n" + "=" * 95)
print("2. calls / call 单独出现")
print("=" * 95)
n2 = 0
for pname, body in PASSAGES.items():
    for m in re.finditer(r"(?<![A-Za-z<])calls?\s+<<", body):
        n2 += 1
        if n2 <= 15:
            print(f"  [{pname}] @{m.start()}: {body[max(0,m.start()-60):m.start()+140]!r}")
print(f"  共 {n2} 处")

print("\n" + "=" * 95)
print("3. 三重尖括号 <<< 或 >>>")
print("=" * 95)
n3 = 0
for pname, body in PASSAGES.items():
    for m in re.finditer(r"<<<|>>>", body):
        n3 += 1
        if n3 <= 15:
            print(f"  [{pname}] @{m.start()}: {body[max(0,m.start()-70):m.start()+100]!r}")
print(f"  共 {n3} 处")

print("\n" + "=" * 95)
print("4. 未闭合的 <<set / <<if（缺 >>）")
print("=" * 95)
n4 = 0
for pname, body in PASSAGES.items():
    for m in re.finditer(r"<<(set|if|elseif)\s+[^<>]{0,200}$", body, re.M):
        n4 += 1
        if n4 <= 10:
            print(f"  [{pname}] @{m.start()}: {m.group(0)[:150]!r}")
print(f"  共 {n4} 处")
