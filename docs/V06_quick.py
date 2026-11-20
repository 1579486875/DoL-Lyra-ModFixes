"""V06：快速统计 passage 正文里的 /* */（不做 passage 归类）。"""
import html as H
import json
import re
from collections import Counter

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

print("=" * 95)
print("1. 三种注释总量")
print("=" * 95)
print(f"  <!--（HTML，安全）      : {len(re.findall(chr(60)+'!--', g))}")
print(f"  /%（SugarCube，安全）  : {len(re.findall(r'/%', g))}")
print(f"  /*（JS 语法，有风险）   : {len(re.findall(r'/[*]', g))}")
print(f"  <<script>> 块          : {len(re.findall(r'<<script>>', g))}")

# 用「先删掉 script 块」的办法快速判定
no_script = re.sub(r"<<script>>.*?<</script>>", "", g, flags=re.S)
print(f"\n  去掉 script 块后 /* 数量: {len(re.findall(r'/[*]', no_script))}")

print("\n" + "=" * 95)
print("2. 不在 script 块内的 /* */ 样例")
print("=" * 95)
risky = []
for m in re.finditer(r"/\*[^*\n]{0,160}?\*/", no_script):
    risky.append(m.group(0))

print(f"  共 {len(risky)} 处")
seen = set()
cnt = Counter()
for r in risky:
    key = r[:60]
    cnt[key] += 1
for k, c in cnt.most_common(30):
    print(f"    {c:>2}×  {k!r}")

print("\n" + "=" * 95)
print("3. 判断是否真会显示：看这些 /* 的位置")
print("=" * 95)
# 抽样看 3 个的上下文（用 no_script，位置已偏移，但上下文仍有意义）
for m in list(re.finditer(r"/\*[^*\n]{0,160}?\*/", no_script))[:6]:
    print(f"  {no_script[max(0,m.start()-120):m.start()+len(m.group(0))+80]!r}")
    print()

print("=" * 95)
print("4. 关键判据：这些 /* */ 是否在 <<widget>> 里、且 widget 调用时会输出")
print("=" * 95)
# 找所有 widget 定义，看第一行是不是 /*
n_widget_comment = 0
lines_starts = []
for m in re.finditer(r'<<widget\s+"([^"]+)"[^>]*>>\s*\n?\s*(/\*[^\n]{0,100})\n', no_script):
    n_widget_comment += 1
    if len(lines_starts) < 20:
        lines_starts.append((m.group(1), m.group(2)[:70]))

print(f"  widget 第一行是 /* 的: {n_widget_comment}")
for w, c in lines_starts:
    print(f"    [{w}] {c!r}")

with open(r"E:\TAML\_dol\work\_risky_comments.json", "w", encoding="utf-8") as f:
    json.dump(risky[:300], f, ensure_ascii=False, indent=1)
print(f"\n  已保存（{len(risky)} 条）")
