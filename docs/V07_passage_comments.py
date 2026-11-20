"""V07：精确统计 passage 正文里的 /* */（排除 <script> 与 <<script>> 块）。

判据：
  1. 只看 <tw-passagedata>...</tw-passagedata> 的 body
  2. 排除 body 里的 <<script>>...<</script>> 块
  3. 剩下的 /* */ 在 SugarCube 渲染时会被当普通文本输出
"""
import html as H
import json
import re
from collections import Counter

raw = open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace")
g = H.unescape(raw)

PASSAGES = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', g, re.S):
    PASSAGES[m.group(1)] = m.group(2)

print(f"passage 总数: {len(PASSAGES)}")

total = 0
by_passage = Counter()
samples = []

for pname, body in PASSAGES.items():
    # 排除 <<script>> 块
    b = re.sub(r"<<script>>.*?<</script>>", "", body, flags=re.S)
    for m in re.finditer(r"/\*[^*\n]{0,180}?\*/", b):
        total += 1
        by_passage[pname] += 1
        if len(samples) < 40:
            samples.append((pname, m.group(0)[:100]))

print("\n" + "=" * 95)
print(f"passage 正文里的 /* */: {total} 处")
print("=" * 95)

print(f"\n按 passage 分布（前 25）:")
for p, c in by_passage.most_common(25):
    print(f"  {c:>3}  {p}")

print(f"\n样例（前 40，去重）:")
seen = set()
for p, s in samples:
    if s in seen:
        continue
    seen.add(s)
    print(f"  [{p}] {s!r}")

# 关键：哪些在 <<widget>> 里
print("\n" + "=" * 95)
print("其中「在 widget 内的 /* */」（widget 被调用时会输出）")
print("=" * 95)
n_w = 0
w_list = []
for pname, body in PASSAGES.items():
    b = re.sub(r"<<script>>.*?<</script>>", "", body, flags=re.S)
    for wm in re.finditer(r'<<widget\s+"([^"]+)"[^>]*>>(.*?)<</widget>>', b, re.S):
        wname, wbody = wm.group(1), wm.group(2)
        if re.search(r"/\*[^*\n]{0,180}?\*/", wbody):
            n_w += 1
            if len(w_list) < 30:
                # 判断 widget 里是否有 <<silently>>
                has_sil = "<<silently>>" in wbody
                w_list.append((wname, has_sil, len(wbody)))
print(f"  {n_w} 个 widget 里含 /* */")
for w, sil, ln in w_list:
    print(f"    [{w}]  silently={sil}  长度={ln}")

with open(r"E:\TAML\_dol\work\_passage_comments.json", "w", encoding="utf-8") as f:
    json.dump({"total": total, "by_passage": dict(by_passage.most_common(50)),
               "samples": samples[:40]}, f, ensure_ascii=False, indent=1)
print(f"\n已保存 _passage_comments.json")
