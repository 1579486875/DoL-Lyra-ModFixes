"""第 12 轮：零错误层② SugarCube 结构 —— 容器宏配对整个 index。

判据：每种容器宏的开/闭必须严格配对，且嵌套深度非负。
"""
import html
import re
import sys
import zipfile
from collections import Counter

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"

# SugarCube 容器宏：开 -> 闭
PAIRS = [
    ("if", "</if>"),
    ("for", "</for>"),
    ("switch", "</switch>"),
    ("silently", "</silently>"),
    ("capture", "</capture>"),
    ("link", "</link>"),
    ("button", "</button>"),
    ("replace", "</replace>"),
    ("append", "</append>"),
    ("prepend", "</prepend>"),
    ("widget", "</widget>"),
    ("script", "</script>"),
    ("stylesheet", "</stylesheet>"),
    ("nobr", "</nobr>"),
    ("done", "</done>"),
    ("timed", "</timed>"),
    ("forget", "</forget>"),
    ("remember", "</remember>"),
    ("textbox", "</textbox>"),
    ("listbox", "</listbox>"),
    ("cycle", "</cycle>"),
]


def load(p):
    z = zipfile.ZipFile(p)
    return html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


def check(label, g):
    print("=" * 88)
    print(f"{label}")
    print("=" * 88)
    problems = []
    for op, cl in PAIRS:
        # 开标记：<<if ...>> 或 <<if>>
        opens = len(re.findall(r"<<" + re.escape(op) + r"(?:>>|\s)", g))
        closes = g.count("<" + cl + ">")   # 正确：cl 已含 < ，如 "</if>" -> "<</if>>"
        diff = opens - closes
        mark = "✅" if diff == 0 else "❌"
        if diff != 0:
            problems.append((op, opens, closes, diff))
        print(f"  {mark} {op:<12} 开 {opens:>6}  闭 {closes:>6}  差 {diff:+d}")

    # 嵌套深度检查（按出现顺序扫描）
    print("\n--- 嵌套深度（深度不能为负）---")
    pat = re.compile(r"<<(" + "|".join(re.escape(p) for p, _ in PAIRS) + r")(?:>>|\s)|<<(/(" +
                     "|".join(re.escape(p) for p, _ in PAIRS) + r"))>>")
    depth = Counter()
    min_depth = Counter()
    for m in pat.finditer(g):
        if m.group(1):
            depth[m.group(1)] += 1
        elif m.group(3):
            depth[m.group(3)] -= 1
            if depth[m.group(3)] < min_depth[m.group(3)]:
                min_depth[m.group(3)] = depth[m.group(3)]

    for op, _ in PAIRS:
        d = min_depth.get(op, 0)
        mark = "✅" if d >= 0 else "❌"
        if d < 0:
            problems.append((op, "min_depth", d, d))
        print(f"  {mark} {op:<12} 最小深度 {d}")
    return problems


mg = load(APK)
vg = load(VAN)

mp = check("modded", mg)
vp = check("vanilla", vg)

print("\n" + "=" * 88)
print("结论")
print("=" * 88)
print(f"  modded 问题项: {len(mp)}")
for p in mp:
    print(f"    {p}")
print(f"  vanilla 问题项: {len(vp)}")
for p in vp:
    print(f"    {p}")

# modded 独有问题才是我们引入的
m_only = set(x[0] for x in mp) - set(x[0] for x in vp)
if m_only:
    print(f"\n  ⚠️ modded 独有问题宏: {sorted(m_only)}")
    sys.exit(1)
else:
    print("\n  ✅ 无 modded 独有的配对问题")
    sys.exit(0)
