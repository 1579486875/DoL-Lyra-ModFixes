"""AC01（第11轮）：扫 index 里 JS 对象属性的英文（玩家可见的 UI 文本）。

覆盖：
  text: "英文"
  label: "英文"
  desc / description: "英文"
  name: "英文"
  message: "英文"
  hint: "英文"
  title: "英文"
  tooltip: "英文"
  alert("英文")
  confirm("英文")
"""
import html as H
import json
import re
from collections import Counter

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))
gb = H.unescape(__import__("zipfile").ZipFile(
    r"E:\TAML\_dol\archive\DoL-Lyra-0.5.12.13-CHS-modded_20261120-061313_修复arsc可安装.apk"
).read("assets/www/index.html").decode("utf-8", "replace"))

FIELDS = ("text", "label", "desc", "description", "name", "message",
          "hint", "title", "tooltip", "caption", "header")

PAT = re.compile(
    r'\b(?:' + "|".join(FIELDS) + r')\s*:\s*["\'`]([^"\'`]{4,150})["\'`]'
)
PAT_ALERT = re.compile(r'\b(?:alert|confirm|prompt)\s*\(\s*["\'`]([^"\'`]{4,150})["\'`]')

TECH = set("""
html css js png jpg gif svg webp json xml api url http https div span class id style
px em rem vh vw rgb rgba hex base64 npc pc rng hp xp mod passage sugarcube twine twee
save load debug error warning info log true false null undefined color colour
black white red blue green yellow purple orange pink grey gray gold teal brown cyan
left right top bottom center middle none auto normal bold italic underline
small large medium big tiny huge
""".split())


def is_ui_text(s):
    s = s.strip()
    if not s or len(s) < 4:
        return False
    if re.search(r"[\u4e00-\u9fff]", s):
        return False
    if s.startswith("<") or re.search(r"[$`]|=>|\bfunction\b|\bvar\b|\bconst\b|\breturn\b", s):
        return False
    words = re.findall(r"[A-Za-z]{2,}", s)
    if len(words) < 2:
        return False
    if all(w.lower() in TECH for w in words):
        return False
    if re.fullmatch(r"[a-z0-9_\-./]+", s):
        return False
    if re.search(r"\.(png|jpg|gif|css|js|twee|json)$", s, re.I):
        return False
    return True


def collect(t):
    out = Counter()
    for m in PAT.finditer(t):
        v = m.group(1)
        if is_ui_text(v):
            out[v] += 1
    for m in PAT_ALERT.finditer(t):
        v = m.group(1)
        if is_ui_text(v):
            out["[alert] " + v] += 1
    return out


cur = collect(g)
base = collect(gb)

print("=" * 95)
print(f"当前 {sum(cur.values())} 处 / {len(cur)} 种    基线 {sum(base.values())} 处 / {len(base)} 种")
print("=" * 95)

only_cur = {k: v for k, v in cur.items() if k not in base}
print(f"\n只在当前（可能是我引入的）: {len(only_cur)}")
for k in list(only_cur)[:10]:
    print(f"    {k!r}")

print("\n" + "=" * 95)
print("当前全部（按字母序，前 60）")
print("=" * 95)
for k in sorted(cur)[:60]:
    print(f"  {cur[k]:>2}×  {k!r}")

if len(cur) > 60:
    print(f"\n  ... 还有 {len(cur) - 60} 种")

with open(r"E:\TAML\_dol\work\_js_field_en.json", "w", encoding="utf-8") as f:
    json.dump(dict(cur), f, ensure_ascii=False, indent=1)
print(f"\n已保存 _js_field_en.json（{len(cur)} 种）")
