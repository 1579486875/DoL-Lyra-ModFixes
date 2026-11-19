"""第 21-24 轮：<<include>> 目标归属 + widget 参数不足抽查。"""
import html
import re
import zipfile
from collections import Counter

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
print("第 21 轮：<<include>> 目标归属")
print("=" * 94)


def inc_missing(g, blocks):
    out = Counter()
    for m in re.finditer(r"<<include\s+([^\n>]{1,90})>>", g):
        t = m.group(1).strip().strip('"\'')
        if t not in blocks:
            out[t] += 1
    return out


mm = inc_missing(mg, mb)
vm = inc_missing(vg, vb)
print(f"  modded 缺失: {len(mm)}   vanilla 缺失: {len(vm)}")
print(f"  modded 独有: {sorted(set(mm) - set(vm))}")
print(f"  vanilla 独有: {sorted(set(vm) - set(mm))}")
for k, v in mm.items():
    print(f"    {v:>3}  {k!r}")

print("\n" + "=" * 94)
print("第 22 轮：抽查「参数不足」的 widget 是否有兜底")
print("=" * 94)
CHECK = ["canvasstart", "canvasdraw", "listsleepoutfits", "toggleHood", "pushClothingCaption"]
for name in CHECK:
    m = re.search(r'<<widget\s+"' + re.escape(name) + r'"\s*>>(.*?)<</widget>>', mg, re.S)
    if not m:
        print(f"  {name}: 未找到定义")
        continue
    body = m.group(1)
    idx = sorted(set(int(x) for x in re.findall(r"_args\[(\d+)\]", body)))
    has_guard = bool(re.search(r"_args\[\d+\]\s*(?:is\s+undefined|\?\?|\|\|)", body))
    has_default = bool(re.search(r"\?\?|\|\||is undefined", body))
    print(f"\n  {name}: 用到 _args{idx}  有兜底={has_guard or has_default}")
    print(f"    {body[:220]!r}")

print("\n" + "=" * 94)
print("第 23 轮：widget 定义在非 Widgets passage 的归属")
print("=" * 94)


def non_widget_defs(blocks):
    out = []
    for pn, b in blocks.items():
        if pn.startswith("Widgets") or pn in ("StoryInit", "StoryCaption", "StoryMenu"):
            continue
        for m in re.finditer(r'<<widget\s+"([^"]+)"', b):
            out.append((m.group(1), pn))
    return out


mn = non_widget_defs(mb)
vn = non_widget_defs(vb)
print(f"  modded: {len(mn)}   vanilla: {len(vn)}")
print(f"  modded 独有: {sorted(set(mn) - set(vn))[:10]}")

print("\n" + "=" * 94)
print("第 24 轮：passage tags 检查（特殊 passage 的 tags）")
print("=" * 94)
raw = open(MODDED, "rb").read().decode("utf-8", "replace")
tags = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*tags="([^"]*)"', raw):
    tags[html.unescape(m.group(1))] = m.group(2)
special = ["StoryInit", "StoryCaption", "StoryMenu", "StoryTitle", "StorySubtitle"]
for s in special:
    print(f"  {s:<20} tags={tags.get(s, '(无此 passage)')!r}")
