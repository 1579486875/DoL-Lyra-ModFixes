"""BE02（第16轮）：修复loadFiltersMenu的防护逻辑缺陷。

问题：BA02的防护 <<if !_traitObj or !_traitObj.desc>> 
在true分支访问 _traitObj.name，当_traitObj为undefined时仍会报错。

修复：改用安全的多分支条件判断。
"""
import re
import html as H
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, 'rb').read().decode('utf-8', 'replace')
d = H.unescape(data)

# 找到loadFiltersMenu widget
pattern = r'(<<widget "loadFiltersMenu">>)(.*?)(<</widget>>)'
m = re.search(pattern, d, re.S)
if not m:
    print("[BE02] 未找到loadFiltersMenu widget")
    sys.exit(1)

widget_start = m.group(1)
widget_content = m.group(2)
widget_end = m.group(3)

# 查找问题代码模式
old_pattern = r'<<if !_traitObj or !_traitObj\.desc>>\s*<<print _traitObj\.name>>\s*<<else>>\s*<<set _traitDesc to `<span class="black">` \+ _traitObj\.desc'

if not re.search(old_pattern, widget_content):
    print("[BE02] 未找到目标模式，可能已修复或代码结构变化")
    # 尝试更宽松的匹配
    if '!_traitObj or !_traitObj.desc' in widget_content:
        print("[BE02] 找到问题代码，但格式不完全匹配，需要手动检查")
        # 显示相关代码
        lines = widget_content.split('\n')
        for i, line in enumerate(lines):
            if '!_traitObj or !_traitObj.desc' in line:
                print(f"\n找到问题行（行{i}）:")
                for j in range(max(0,i-2), min(len(lines),i+8)):
                    print(f"{j}: {lines[j][:100]}")
    sys.exit(1)

# 替换为安全的多分支逻辑
new_code = '''<<if _traitObj and _traitObj.desc>>
\t\t\t\t\t\t\t\t\t<<set _traitDesc to `<span class="black">` + _traitObj.desc'''

new_widget_content = re.sub(
    old_pattern,
    new_code,
    widget_content
)

if new_widget_content == widget_content:
    print("[BE02] 替换失败，未找到匹配")
    sys.exit(1)

# 构建新的widget
old_widget = widget_start + widget_content + widget_end
new_widget = widget_start + new_widget_content + widget_end

d = d.replace(old_widget, new_widget)

# 写回
data = data.replace(
    H.escape(H.unescape(data), quote=False),
    H.escape(d, quote=False)
)

open(HTML, 'wb').write(data.encode('utf-8'))
print("[BE02] 已修复loadFiltersMenu的防护逻辑")
print("[BE02] 修改：<<if !_traitObj or !_traitObj.desc>> → <<if _traitObj and _traitObj.desc>>")
print("[BE02] 效果：只在_traitObj完整存在时才访问.desc，避免undefined错误")
