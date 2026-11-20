"""E05：精确判据 —— 只找「标识符 + 中文 + 全角句号」这种把 . 翻成 。 的情况。"""
import html as H
import re

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(data)

print("=" * 100)
print("精确判据：标识符[中文]。 （点号被翻成句号）")
print("=" * 100)

# 只看宏内部：<<set/if/elseif/run/switch/case>> 的非字符串部分
BAD = []
for m in re.finditer(r"<<(if|elseif|set|run|switch|case|for|while)\b([^<>]{0,800}?)>>", g):
    body = m.group(2)
    # 挖掉字符串字面量
    stripped = re.sub(r'"[^"]*"|\'[^\']*\'|`[^`]*`', lambda mm: " " * len(mm.group(0)), body)
    # 挖掉正则字面量
    stripped = re.sub(r"/[^/\n]*/", lambda mm: " " * len(mm.group(0)), stripped)
    # 找 中文
    if not re.search(r"[\u4e00-\u9fff]", stripped):
        continue
    BAD.append((m.start(), m.group(0), stripped))

print(f"  命中 {len(BAD)} 处\n")
for pos, full, stripped in BAD:
    print(f"  @{pos}")
    print(f"    原文  : {full[:250]!r}")
    print(f"    去字符串: {stripped[:250]!r}")
    print()

print("=" * 100)
print("所有「中文 + 全角句号」在宏内的（点号嫌疑）")
print("=" * 100)
n = 0
for m in re.finditer(r"<<(if|elseif|set|run|switch|case|for|while)\b([^<>]{0,800}?)>>", g):
    body = m.group(2)
    stripped = re.sub(r'"[^"]*"|\'[^\']*\'|`[^`]*`', lambda mm: " " * len(mm.group(0)), body)
    stripped = re.sub(r"/[^/\n]*/", lambda mm: " " * len(mm.group(0)), stripped)
    for mm in re.finditer(r"[\u4e00-\u9fff]+。", stripped):
        n += 1
        print(f"  @{m.start()}: {mm.group(0)!r}  in  {m.group(0)[:200]!r}")
print(f"\n  共 {n} 处")
