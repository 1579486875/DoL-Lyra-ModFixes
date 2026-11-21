"""BD02（第17轮）：修复Forest Shop的$gwylanSeen未初始化问题。

问题：$gwylanSeen.includes()调用时变量未定义
修复：在forestShop-main widget开头添加初始化代码
"""
import re
import html as H
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, 'rb').read().decode('utf-8', 'replace')
d = H.unescape(data)

# 找到forestShop-main widget
pattern = r'(<<widget "forestShop-main">>)(.*?)(<</widget>>)'
m = re.search(pattern, d, re.S)
if not m:
    print("[BD02] 未找到forestShop-main widget")
    sys.exit(1)

widget_start = m.group(1)
widget_content = m.group(2)
widget_end = m.group(3)

# 检查是否已经有初始化
if '$gwylanSeen' in widget_content[:200] and ('<<set $gwylanSeen' in widget_content[:200] or 'gwylanSeen to' in widget_content[:200]):
    print("[BD02] $gwylanSeen已经初始化，无需修改")
    sys.exit(0)

# 在widget开头添加初始化代码
init_code = '''
/* BD02: 初始化$gwylanSeen数组，防止.includes()报错 */
<<if $gwylanSeen is undefined>>
\t<<set $gwylanSeen to []>>
<</if>>
'''

new_widget_content = init_code + widget_content

# 替换
old_widget = widget_start + widget_content + widget_end
new_widget = widget_start + new_widget_content + widget_end

d = d.replace(old_widget, new_widget)

# 写回
data = data.replace(
    H.escape(H.unescape(data), quote=False),
    H.escape(d, quote=False)
)

open(HTML, 'wb').write(data.encode('utf-8'))
print("[BD02] 已在forestShop-main widget开头添加$gwylanSeen初始化代码")
print("[BD02] 修复：防止TypeError: Cannot read properties of undefined (reading 'includes')")
