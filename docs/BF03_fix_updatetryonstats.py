"""BF03（第17轮）：修复updatetryonstats的元素缺失防护。

问题：
在Clothing Shop等没有tryonstats-div的passage中调用updatetryonstats会报错。

修复：
添加元素存在性检查，避免在元素不存在时报错。
"""
import re
import html as H
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, 'rb').read().decode('utf-8', 'replace')
d = H.unescape(data)

print("[BF03] 修复updatetryonstats元素缺失防护\n")

# 找到updatetryonstats widget
widget_pattern = r'(<<widget\s+["\']updatetryonstats["\']>>)(.*?)(<</widget>>)'
m = re.search(widget_pattern, d, re.S | re.I)

if not m:
    print("[BF03] ❌ 未找到updatetryonstats widget")
    sys.exit(1)

widget_start = m.group(1)
widget_content = m.group(2)
widget_end = m.group(3)

print(f"找到widget，当前内容（{len(widget_content)}字符）:")
print(widget_content.strip())

# 检查是否已经修复过
if 'length' in widget_content.lower() or 'if' in widget_content:
    print("\n[BF03] ⚠️  widget已包含条件检查，可能已修复")
    print("当前实现:")
    print(widget_content.strip())
    sys.exit(0)

# 新的安全实现
new_content = '''
	<<run 
		var el = $("#tryonstats-div");
		if(el.length > 0){
			el.empty().wiki("<<tryOnStats>>");
		}
	>>
'''

# 构建新的widget
old_widget = widget_start + widget_content + widget_end
new_widget = widget_start + new_content + widget_end

# 替换
d_new = d.replace(old_widget, new_widget)

if d_new == d:
    print("\n[BF03] ❌ 替换失败，未找到匹配")
    sys.exit(1)

# 写回
data_new = data.replace(
    H.escape(d, quote=False),
    H.escape(d_new, quote=False)
)

open(HTML, 'wb').write(data_new.encode('utf-8'))

print("\n[BF03] ✅ 已修复updatetryonstats")
print("修改前:")
print(widget_content.strip())
print("\n修改后:")
print(new_content.strip())
print("\n效果：元素不存在时静默跳过，不报错")
