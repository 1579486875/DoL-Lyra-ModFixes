"""第 14-20 轮：widget 定义重复 / 覆盖顺序 / 递归 / 参数错位。

14) 同名 widget 被定义多次（后定义覆盖前定义）
15) 模组新增 widget 是否与本体重名
16) widget 递归调用
17) <<include>> / <<display>> 的目标 passage 是否存在
18) widget 调用时参数个数（<<widget>> 用 _args）
19) widget 定义在 passage 里的位置（必须早于调用）
20) <<widget>> 内部再定义 <<widget>>
"""
import html
import re
import zipfile
from collections import Counter, defaultdict

MODDED = r"E:\TAML\_dol\work\index_modded6.html"
VANILLA = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(path):
    if path.endswith(".apk"):
        z = zipfile.ZipFile(path)
        raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    else:
        raw = open(path, "rb").read().decode("utf-8", "replace")
    blocks = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        blocks[html.unescape(m.group(1))] = html.unescape(m.group(2))
    return blocks, html.unescape(raw)


mb, mg = load(MODDED)
vb, vg = load(VANILLA)

print("=" * 94)
print("第 14 轮：同名 widget 被定义多次")
print("=" * 94)


def widget_defs(blocks):
    d = defaultdict(list)
    for pn, b in blocks.items():
        for m in re.finditer(r'<<widget\s+"([^"]+)"', b):
            d[m.group(1)].append(pn)
    return d


md = widget_defs(mb)
vd = widget_defs(vb)
m_dup = {k: v for k, v in md.items() if len(v) > 1}
v_dup = {k: v for k, v in vd.items() if len(v) > 1}
print(f"  modded 重复定义: {len(m_dup)}   vanilla: {len(v_dup)}")
for k, v in sorted(m_dup.items(), key=lambda x: -len(x[1]))[:12]:
    mark = "（新增）" if k not in vd else ""
    print(f"    {k:<34} {len(v)} 次 {v[:3]} {mark}")

new_dup = set(m_dup) - set(v_dup)
print(f"\n  modded 独有重复: {sorted(new_dup)}")

print("\n" + "=" * 94)
print("第 15 轮：模组新增 widget 与本体重名")
print("=" * 94)
new_widgets = set(md) - set(vd)
print(f"  新增 widget: {len(new_widgets)} -> {sorted(new_widgets)}")
lost = set(vd) - set(md)
print(f"  丢失 widget: {len(lost)} -> {sorted(lost)}")

print("\n" + "=" * 94)
print("第 16 轮：widget 内部再定义 widget")
print("=" * 94)
nested_defs = []
for pn, b in mb.items():
    for m in re.finditer(r'<<widget\s+"([^"]+)"\s*>>(.*?)<</widget>>', b, re.S):
        if "<<widget" in m.group(2):
            nested_defs.append((pn, m.group(1)))
print(f"  嵌套定义: {len(nested_defs)}")
for x in nested_defs[:8]:
    print(f"    {x}")

print("\n" + "=" * 94)
print("第 17 轮：<<include>> / <<display>> 目标")
print("=" * 94)
for tag in ("include", "display"):
    targets = Counter()
    for m in re.finditer(r"<<" + tag + r"\s+([^\n>]{1,80})>>", mg):
        targets[m.group(1).strip()] += 1
    miss = [t for t in targets if t.strip('"\'') not in mb and not t.startswith(("$", "_", "`"))]
    print(f"  <<{tag}>>: {sum(targets.values())} 处，目标不存在 {len(miss)}")
    for t in miss[:8]:
        print(f"    {t!r}")

print("\n" + "=" * 94)
print("第 18 轮：widget 调用参数个数 vs 定义里 _args 使用")
print("=" * 94)
# 统计每个 widget 定义里用了 _args[N] 的最大 N
maxarg = {}
for name, reps in md.items():
    for pn in reps:
        b = mb[pn]
        m = re.search(r'<<widget\s+"' + re.escape(name) + r'"\s*>>(.*?)<</widget>>', b, re.S)
        if not m:
            continue
        body = m.group(1)
        idx = [int(x) for x in re.findall(r"_args\[(\d+)\]", body)]
        if idx:
            maxarg[name] = max(idx) + 1

print(f"  用到 _args 的 widget: {len(maxarg)}")
# 抽样检查调用时参数是否足够（只看单行调用）
short = []
for name, need in list(maxarg.items())[:200]:
    for m in re.finditer(r"<<" + re.escape(name) + r"\b([^>]*)>>", mg):
        args = m.group(1).strip()
        # 粗略计数：按空格 + 引号分组
        cnt = 0
        if args:
            cnt = len(re.findall(r"""(?:"[^"]*"|'[^']*'|`[^`]*`|\S+)""", args))
        if cnt < need:
            short.append((name, need, cnt, args[:60]))
            break
print(f"  参数可能不足的: {len(short)}")
for x in short[:12]:
    print(f"    {x[0]} 需要 {x[1]} 给了 {x[2]}  args={x[3]!r}")

print("\n" + "=" * 94)
print("第 19-20 轮：widget 定义 passage 是否可能晚于调用")
print("=" * 94)
# SugarCube 的 <<widget>> 在 StoryInit 前解析，所以只要在 passage 里就 OK
# 检查是否有 widget 定义在非 Widgets* 的普通剧情 passage 里（可能未被解析）
non_widget_passages = []
for name, reps in md.items():
    for pn in reps:
        if not (pn.startswith("Widgets") or pn in ("StoryInit", "StoryCaption")):
            non_widget_passages.append((name, pn))
print(f"  定义在非 Widgets passage 的: {len(non_widget_passages)}")
for x in non_widget_passages[:10]:
    print(f"    {x}")
