"""V05：统计 passage 正文里的 /* */ 注释（SugarCube 里不是注释，会显示）。

区分三种：
  <!-- ... -->   HTML 注释        → 安全
  /% ... %/      SugarCube 注释   → 安全
  /* ... */      JS 注释语法      → ❌ 在 passage 正文里会原样输出
    但在 <<script>> 块内是安全的（那里是真正的 JS）
"""
import html as H
import re
from collections import Counter

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

PASSAGES = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', g, re.S):
    PASSAGES[m.group(1)] = m.group(2)

print("=" * 95)
print("1. 三种注释的总量")
print("=" * 95)
print(f"  <!-- -->（HTML，安全）: {len(re.findall(r'<!--', g))}")
print(f"  /% %/（SugarCube，安全）: {len(re.findall(r'/%', g))}")
print(f"  /* */（风险）: {len(re.findall(r'/\*', g))}")
print(f"  <<script>> 块数: {len(re.findall(r'<<script>>', g))}")

print("\n" + "=" * 95)
print("2. 在「不在 <<script>> 块内」的 /* */ —— 这些会显示")
print("=" * 95)

# 先把所有 <<script>> 块的位置标出来
script_ranges = [(m.start(), m.end()) for m in re.finditer(r"<<script>>.*?<</script>>", g, re.S)]


def in_script(pos):
    for s, e in script_ranges:
        if s <= pos < e:
            return True
    return False


risky = []
for m in re.finditer(r"/\*[^*]{0,200}?\*/", g):
    if in_script(m.start()):
        continue
    risky.append((m.start(), m.group(0)))

print(f"  不在 script 块内的 /* */: {len(risky)}")

# 按所属 passage 归类
by_passage = Counter()
samples = []
for pos, txt in risky:
    # 找它属于哪个 passage
    for pname, body in PASSAGES.items():
        idx = g.find('name="' + pname + '"')
        # 简化：用最近的 <tw-passagedata
        pass
    samples.append(txt[:90])

# 直接用 passage 区间判断
p_ranges = []
for m in re.finditer(r'<tw-passagedata name="([^"]*)"[^>]*>', g):
    p_ranges.append((m.start(), m.group(1)))


def which_passage(pos):
    cur = None
    for s, n in p_ranges:
        if s <= pos:
            cur = n
        else:
            break
    return cur


pc = Counter()
for pos, txt in risky:
    pc[which_passage(pos)] += 1

print(f"\n  按 passage 分布（前 20）:")
for p, c in pc.most_common(20):
    print(f"    {c:>3}  {p}")

print(f"\n  样例（前 25）:")
for txt in samples[:25]:
    print(f"    {txt!r}")

# 保存
import json
with open(r"E:\TAML\_dol\work\_risky_comments.json", "w", encoding="utf-8") as f:
    json.dump([{"pos": p, "passage": which_passage(p), "text": t} for p, t in risky],
              f, ensure_ascii=False, indent=1)
print(f"\n  已保存 _risky_comments.json（{len(risky)} 条）")

print("\n" + "=" * 95)
print("3. 验证：leash 的调用点是否在 <<silently>> 里")
print("=" * 95)
calls = list(re.finditer(r"<<leash\b", g))
print(f"  <<leash>> 调用 {len(calls)} 次")
for m in calls[:5]:
    ctx = g[max(0, m.start() - 300):m.start() + 100]
    has_sil = "<<silently>>" in ctx
    print(f"    @{m.start()}  前置有 silently: {has_sil}")
    print(f"      {ctx[-260:]!r}")
