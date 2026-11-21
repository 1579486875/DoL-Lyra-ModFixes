"""BC02（改进版）：精确修复玩具名称显示翻译。

策略：在设置玩具名称变量（_toyt/$_toy等）后，立即添加翻译调用。
目标模式：<<set _toyt to $NPCList[_n].lefttool>> 后添加 <<set _toyt to toyNameCN(_toyt)>>
"""
import html as H
import os
import re
import sys

HTML = os.environ.get("DOL_HTML") or r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(data)

count = 0

# 模式1：<<set _toyt to ... lefttool/righttool>>
# 在这之后添加：<<set _toyt to toyNameCN(_toyt)>>
pattern1 = r'(<<set _toyt to \(_args\[0\] is "left" \? \$NPCList\[_n\]\.lefttool : \$NPCList\[_n\]\.righttool\)>>)'
replacement1 = r'\1<<set _toyt to toyNameCN(_toyt)>>'

matches1 = list(re.finditer(pattern1, g))
if matches1:
    print(f"[BC02] 找到{len(matches1)}处 _toyt 赋值")
    for m in matches1:
        old = m.group(0)
        new = re.sub(pattern1, replacement1, old)
        g = g.replace(old, new, 1)
        count += 1

# 模式2：直接在文本中的 $_toy（但需要确保是显示上下文）
# 先不处理，因为$_toy可能已经被处理过

# 模式3：<<set $tooltarget to "...">> 之后的使用
# 这个更复杂，暂时跳过

if count > 0:
    data = data.replace(H.escape(H.unescape(data), quote=False), H.escape(g, quote=False))
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"[BC02] 已修改{count}处玩具名称显示，添加toyNameCN翻译")
else:
    print("[BC02] 未找到匹配的模式，可能需要更精确的分析")
    sys.exit(1)
