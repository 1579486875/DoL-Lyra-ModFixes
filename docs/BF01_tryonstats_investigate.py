"""BF01（第17轮）：调查updatetryonstats错误。

用户报告：
<<replace>>: no elements matched the selector "#tryonstats-div"
"""
import re
import html as H

HTML = r"E:\TAML\_dol\work\index_modded6.html"
d = H.unescape(open(HTML, 'rb').read().decode('utf-8', 'replace'))

print("[BF01] 调查updatetryonstats错误\n")

# 1. 搜索tryonstats-div元素定义
div_pattern = r'id\s*=\s*["\']tryonstats-div["\']'
div_matches = re.findall(div_pattern, d)
print(f"1. 找到 id=\"tryonstats-div\" 元素定义: {len(div_matches)} 处")

# 2. 搜索updatetryonstats widget
widget_pattern = r'<<widget\s+["\']updatetryonstats["\']>>(.*?)<</widget>>'
m = re.search(widget_pattern, d, re.S | re.I)
if m:
    content = m.group(1)
    print(f"\n2. 找到 updatetryonstats widget: {len(content)} 字符")
    # 显示前800字符
    print("内容片段:")
    print(content[:800])
else:
    print("\n2. ❌ 未找到 updatetryonstats widget")

# 3. 搜索所有<<replace>>指向tryonstats的
replace_pattern = r'<<replace\s+["\']#tryonstats-div["\']>>'
replace_matches = re.findall(replace_pattern, d, re.I)
print(f"\n3. 找到 <<replace \"#tryonstats-div\">>: {len(replace_matches)} 处")

# 4. 搜索调用updatetryonstats的地方
call_pattern = r'<<updatetryonstats>>'
call_matches = re.findall(call_pattern, d, re.I)
print(f"\n4. 找到 <<updatetryonstats>> 调用: {len(call_matches)} 处")

# 5. 总体引用统计
total_refs = len(re.findall(r'tryonstats', d, re.I))
print(f"\n5. \"tryonstats\" 总引用次数: {total_refs}")

print("\n[BF01] 调查完成")
