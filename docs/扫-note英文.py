# -*- coding: utf-8 -*-
"""扫所有 <<note "英文" ...>> 硬编码，看还有多少未翻译的。"""
import re
from collections import Counter

h = open(r"E:\TAML\_dol\work\index_modded6.html", encoding="utf-8").read()

# index 里 passage 内容是 HTML 转义的：<< -> &lt;&lt;  >> -> &gt;&gt;
# 但引号保持原样
PAT = re.compile(r'&lt;&lt;note\s+"([^"]*)"(?:\s+"([^"]*)")?\s*&gt;&gt;')

hits = Counter()
plain = Counter()
for m in PAT.finditer(h):
    txt = m.group(1)
    hits[txt] += 1
    # 判断是否含中文
    if not re.search(r"[\u4e00-\u9fff]", txt):
        plain[txt] += 1

print("=== 全部 <<note>> 参数（共 %d 种 / %d 处）===" % (len(hits), sum(hits.values())))
for t, c in hits.most_common(40):
    mark = "" if re.search(r"[\u4e00-\u9fff]", t) else "   ← 纯英文"
    print("  %-46s x%-3d%s" % (t[:44], c, mark))

print("\n=== 纯英文的（需要处理）===")
if plain:
    for t, c in plain.most_common():
        print("  %-46s x%d" % (t, c))
else:
    print("  无")

print("\n=== 总计 ===")
print("  纯英文种类: %d / 总数 %d 处" % (len(plain), sum(plain.values())))
