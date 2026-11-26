# -*- coding: utf-8 -*-
"""替换 <<note "Escape Attempt" "red">> 为中文。"""
import re

P = r"E:\TAML\_dol\work\index_modded6.html"
h = open(P, encoding="utf-8").read()

# index 里 passage 内容是 HTML 转义的
OLD = '&lt;&lt;note "Escape Attempt" "red"&gt;&gt;'
NEW = '&lt;&lt;note "逃脱尝试" "red"&gt;&gt;'

n = h.count(OLD)
print("找到目标串:", n, "处")
if n == 0:
    # 诊断：列出所有 Escape Attempt 的上下文
    for mm in re.finditer(r"Escape Attempt", h):
        print("  @%d: %r" % (mm.start(), h[max(0, mm.start() - 60):mm.start() + 50]))
    raise SystemExit(1)

h2 = h.replace(OLD, NEW)
open(P, "w", encoding="utf-8").write(h2)

print("✅ 已替换 %d 处" % n)
print("   剩余 Escape Attempt 总数:", h2.count("Escape Attempt"))

# 确认 JS 里的 case 标签没被误改
js_case = len(re.findall(r"Whitney Bully Parasite Event Escape Attempt", h2))
print("   JS case 标签保留:", js_case, "处（应为 1）")

# 确认新的中文 note 存在
print("   新 note 数量:", h2.count(NEW))
