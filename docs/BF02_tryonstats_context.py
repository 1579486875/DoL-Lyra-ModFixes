"""BF02：深入调查tryonstats在Clothing Shop的上下文。"""
import re
import html as H

HTML = r"E:\TAML\_dol\work\index_modded6.html"
d = H.unescape(open(HTML, 'rb').read().decode('utf-8', 'replace'))

print("[BF02] 深入调查tryonstats上下文\n")

# 1. 找到Clothing Shop passage
shop_pattern = r'::.*?Clothing\s+Shop.*?::(.*?)(?=::|\Z)'
m = re.search(shop_pattern, d, re.S | re.I)
if m:
    shop_content = m.group(1)
    print(f"1. 找到Clothing Shop passage: {len(shop_content)} 字符")
    
    # 检查是否有tryonstats-div定义
    if 'tryonstats-div' in shop_content:
        print("   ✅ 包含tryonstats-div定义")
        # 显示定义位置
        lines = shop_content.split('\n')
        for i, line in enumerate(lines):
            if 'tryonstats-div' in line:
                print(f"   行{i}: {line.strip()[:100]}")
    else:
        print("   ❌ 不包含tryonstats-div定义")
    
    # 检查是否调用updatetryonstats
    if '<<updatetryonstats>>' in shop_content.lower():
        print("   ✅ 调用了updatetryonstats")
        # 显示调用位置
        lines = shop_content.split('\n')
        for i, line in enumerate(lines):
            if 'updatetryonstats' in line.lower():
                print(f"   行{i}: {line.strip()[:100]}")
                # 显示前后各3行
                start = max(0, i-3)
                end = min(len(lines), i+4)
                print("   上下文:")
                for j in range(start, end):
                    marker = ">>> " if j == i else "    "
                    print(f"{marker}{j}: {lines[j][:120]}")
    else:
        print("   ❌ 未调用updatetryonstats")
else:
    print("1. ❌ 未找到Clothing Shop passage")

# 2. 查看所有tryonstats-div定义的上下文
print("\n2. 所有tryonstats-div定义的位置:")
div_pattern = r'id\s*=\s*["\']tryonstats-div["\']'
for m in re.finditer(div_pattern, d):
    pos = m.start()
    # 获取前后200字符
    start = max(0, pos - 200)
    end = min(len(d), pos + 200)
    context = d[start:end]
    # 查找最近的passage名称
    passage_pattern = r'::\s*([^:]+?)\s*::'
    passages = re.findall(passage_pattern, d[max(0, pos-5000):pos])
    if passages:
        current_passage = passages[-1]
        print(f"   在passage: {current_passage}")
    else:
        print(f"   在未知位置")
    print(f"   上下文: ...{context[180:220]}...")

print("\n[BF02] 调查完成")
