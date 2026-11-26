# -*- coding: utf-8 -*-
"""定位 Widgets variablesStatic 里的裸尖括号。"""
import html as H
import re

h = open(r"E:\TAML\_dol\work\index_modded6.html", encoding="utf-8").read()

m = re.search(r'<tw-passagedata[^>]*name="Widgets variablesStatic"[^>]*>(.*?)</tw-passagedata>', h, re.S)
if not m:
    print("❌ 未找到 passage")
    raise SystemExit(1)

body = m.group(1)
print("passage 长度: %d" % len(body))

# 找裸 < 和 >
print("\n=== 裸尖括号（排除已转义的 &lt; &gt; 和 HTML 标签）===")
# 先找所有 < 但不是 &lt;
for mm in re.finditer(r"<", body):
    i = mm.start()
    # 排除 &lt; 里的（不会匹配到，因为 &lt; 是 & l t ;）
    ctx = body[max(0, i - 120):i + 160]
    print("\n@%d: %s" % (i, ctx.replace("\n", " ")[:300]))

print("\n\n=== 裸 > 的数量 ===")
print("  < 数量:", body.count("<"))
print("  > 数量:", body.count(">"))
print("  &lt; 数量:", body.count("&lt;"))
print("  &gt; 数量:", body.count("&gt;"))

# 找出我插入的 DESCCN_CONCAT_FIX 附近
i = body.find("DESCCN_CONCAT_FIX")
if i >= 0:
    print("\n=== DESCCN_CONCAT_FIX 附近 (%d) ===" % i)
    print(body[max(0, i - 200):i + 2500])
