"""分析：i18n 里哪些条目适合「不看 pos 的全量替换」。

判据（保守）：
  - f 长度 >= 6（太短的容易误伤）
  - f 里含空格或标点（说明是自然语言片段，不是标识符）
  - f 不含 << >> $ _ 等代码字符
  - t 与 f 不同
  - f 在全库出现次数可控（<= 50）
"""
import html
import json
import re
from collections import Counter

HTML = r"E:\TAML\_dol\work\index_modded6.html"
I18N = r"E:\TAML\_dol\work\i18n_dict.json"

g = html.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
d = json.load(open(I18N, "r", encoding="utf-8"))
items = d["typeB"]["TypeBInputStoryScript"]

print(f"i18n 条目总数: {len(items)}")

SAFE = []
SKIP_TOO_SHORT = SKIP_CODE = SKIP_NOT_FOUND = 0

for it in items:
    f, t = it.get("f"), it.get("t")
    if not f or t is None or f == t:
        continue
    # 已在中：跳过
    if f not in g:
        SKIP_NOT_FOUND += 1
        continue
    # 代码字符
    if re.search(r"[<>$`{}]", f):
        SKIP_CODE += 1
        continue
    # 太短
    if len(f) < 6:
        SKIP_TOO_SHORT += 1
        continue
    # 必须是自然语言（含空格或标点）
    if not re.search(r"[\s,.!?;:'\"]", f):
        SKIP_CODE += 1
        continue
    SAFE.append(it)

print(f"\n可安全全量替换: {len(SAFE)} 条")
print(f"  跳过（原文已不在）: {SKIP_NOT_FOUND}")
print(f"  跳过（代码字符/无空格）: {SKIP_CODE}")
print(f"  跳过（太短）: {SKIP_TOO_SHORT}")

# 统计这些条目在 index 里的出现次数
print("\n=== 出现次数分布 ===")
cnt_dist = Counter()
for it in SAFE:
    f = it["f"]
    n = g.count(f)
    cnt_dist[min(n, 10)] += 1
for k in sorted(cnt_dist):
    label = f"{k}" if k < 10 else "10+"
    print(f"  {label:>3} 次: {cnt_dist[k]:>5} 条")

print("\n=== 示例 20 条 ===")
for it in SAFE[:20]:
    f, t = it["f"], it["t"]
    n = g.count(f)
    print(f"  [{n:>2}次] {f[:60]!r}")
    print(f"         -> {t[:60]!r}")

# 估算：全量替换能多翻多少字
gain = 0
for it in SAFE:
    f, t = it["f"], it["t"]
    n = g.count(f)
    cjk_t = len(re.findall(r"[\u4e00-\u9fff]", t))
    cjk_f = len(re.findall(r"[\u4e00-\u9fff]", f))
    gain += n * (cjk_t - cjk_f)
print(f"\n估算可增加中文字符: {gain:+,}")
