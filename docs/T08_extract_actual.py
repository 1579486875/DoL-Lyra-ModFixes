"""T08：提取 Template.add 里所有仍是英文的字符串（按实际文本，保留转义）。"""
import html as H
import json
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

# 定位所有 Template.add 块
BLOCKS = []
for m in re.finditer(r'Template\.add\(\s*"([^"]+)"\s*,\s*', g):
    start = m.end()
    i = start
    depth = 1
    while i < len(g) and depth > 0:
        if g[i] == "(":
            depth += 1
        elif g[i] == ")":
            depth -= 1
        i += 1
    BLOCKS.append((m.group(1), start, i))

print(f"Template.add 块数: {len(BLOCKS)}\n")

out = {}
for name, s, e in BLOCKS:
    blk = g[s:e]
    # 提取所有双引号字符串（保留原样，含反斜杠转义）
    strs = re.findall(r'"((?:[^"\\]|\\.)*)"', blk)
    en = []
    for raw in strs:
        plain = raw.replace("\\'", "'").replace('\\"', '"')
        if re.search(r"[\u4e00-\u9fff]", plain):
            continue
        if len(re.findall(r"[A-Za-z]{2,}", plain)) < 2:
            continue
        if re.fullmatch(r"[a-z_]+", plain):     # 纯小写单词（多为变量/键）
            continue
        en.append(raw)                            # ← 保留原始转义形态
    if en:
        out[name] = en
        print("=" * 95)
        print(f"[?{name}]  英文 {len(en)} 条")
        print("=" * 95)
        for r in en:
            print(f"    {r!r}")

with open(r"E:\TAML\_dol\work\_tpl_actual.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

total = sum(len(v) for v in out.values())
print(f"\n{'=' * 95}")
print(f"英文总计: {total} 条，跨 {len(out)} 个模板")
print("已保存 _tpl_actual.json")
