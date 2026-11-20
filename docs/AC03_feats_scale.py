"""AC03：统计成就系统规模 + 提取成就名/描述，决定翻译范围。"""
import html as H
import json
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

print("=" * 95)
print("1. 找成就对象的定义位置")
print("=" * 95)
# 成就对象的特征：{ title: "...", desc: "...", difficulty: N, filter: [...] }
feat_count = len(re.findall(r'difficulty:\s*\d+,\s*series:', g))
print(f"  含 difficulty + series 的对象: {feat_count} 个")

# 找容器名
for pat in (r"setup\.feats\s*=\s*\{", r"var\s+feats\s*=\s*\{",
            r"setup\.achievements\s*=\s*\{", r"AllFeats\s*=\s*\{"):
    n = len(re.findall(pat, g))
    print(f"  {pat!r}: {n}")

print("\n" + "=" * 95)
print("2. 提取成就的 title / desc / hint")
print("=" * 95)
# 在 setup.feats = { ... } 里提取
m = re.search(r"setup\.feats\s*=\s*\{", g)
if m:
    # 取到匹配的 }
    i = m.end()
    depth = 1
    while i < len(g) and depth > 0 and i < m.end() + 400000:
        if g[i] == "{":
            depth += 1
        elif g[i] == "}":
            depth -= 1
        i += 1
    block = g[m.start():i]

    titles = re.findall(r'title:\s*"((?:[^"\\]|\\.)*)"', block)
    descs = re.findall(r'\bdesc:\s*"((?:[^"\\]|\\.)*)"', block)
    hints = re.findall(r'\bhint:\s*"((?:[^"\\]|\\.)*)"', block)

    print(f"  title: {len(titles)} 条")
    print(f"  desc:  {len(descs)} 条")
    print(f"  hint:  {len(hints)} 条")

    print(f"\n  样例（前 15 个 title）:")
    for t in titles[:15]:
        print(f"    {t!r}")

    print(f"\n  样例（前 10 个 desc）:")
    for d in descs[:10]:
        print(f"    {d!r}")

    print(f"\n  样例（前 5 个 hint）:")
    for h_ in hints[:5]:
        print(f"    {h_!r}")

    # 统计有多少已含中文
    cn_t = sum(1 for t in titles if re.search(r"[\u4e00-\u9fff]", t))
    cn_d = sum(1 for d in descs if re.search(r"[\u4e00-\u9fff]", d))
    cn_h = sum(1 for x in hints if re.search(r"[\u4e00-\u9fff]", x))
    print(f"\n  已含中文: title {cn_t} / desc {cn_d} / hint {cn_h}")

    with open(r"E:\TAML\_dol\work\_feats.json", "w", encoding="utf-8") as f:
        json.dump({"titles": titles, "descs": descs, "hints": hints},
                  f, ensure_ascii=False, indent=1)
    print(f"\n  已保存 _feats.json")
else:
    print("  ❌ 找不到 setup.feats = {")

print("\n" + "=" * 95)
print("3. 服装描述的规模")
print("=" * 95)
n_desc = len(re.findall(r'description:\s*"', g))
print(f"  description: 字段 {n_desc} 个")
