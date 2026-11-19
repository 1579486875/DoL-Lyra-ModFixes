"""补回 babyRentDisplay 丢失的第 3 个参数（颜色）。

vanilla: <<babyRentDisplay " plus " " for not..." "gold">>
modded : <<babyRentDisplay "还有代替你照顾孩子的" "">>        <- 丢参数

定义: <<printmoney $babyRent _args[2]>>
"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

data = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(data)

print("=" * 90)
print("当前所有 babyRentDisplay 调用")
print("=" * 90)
for m in re.finditer(r'<<babyRentDisplay([^>]{0,200})>>', g):
    print(f"  {m.group(0)!r}")

print("\n" + "=" * 90)
print("修复：补第 3 参数")
print("=" * 90)
total = 0

# 模式：<<babyRentDisplay "A" "">> 或 <<babyRentDisplay "A">>
# 需要补一个颜色。默认 gold（贝利租金在原版多为 gold）
def fix_one(match):
    global total
    inner = match.group(1)
    # 数参数个数
    args = re.findall(r'"(?:[^"\\]|\\.)*"', inner)
    if len(args) >= 3:
        return match.group(0)
    # 判断上下文颜色：pink 常出现在"威胁"语境内
    start = match.start()
    ctx = g[max(0, start - 300):start + 300]
    color = "pink" if "pink" in ctx else "gold"
    total += 1
    return f'<<babyRentDisplay{inner} "{color}">>'

new_g = re.sub(r'<<babyRentDisplay([^>]{0,200})>>', fix_one, g)
print(f"补了 {total} 处")

if total:
    # 写回转义形态
    # g 是反转义的，直接整体重新转义会破坏原有实体……
    # 改为：在原始 data 上做同样的替换
    def fix_raw(match):
        inner = match.group(1)
        args = re.findall(r'&quot;(?:[^&]|&(?!quot;))*&quot;', inner)
        # 原始里引号是原样的
        args2 = re.findall(r'"(?:[^"\\]|\\.)*"', inner)
        if len(args2) >= 3:
            return match.group(0)
        gpos = match.start()
        ctx = data[max(0, gpos - 350):gpos + 350]
        color = "pink" if "&quot;" in ctx and "pink" in ctx else "gold"
        return f'<<babyRentDisplay{inner} "{color}">>'

    # 原始 data 里宏是 &lt;&lt; 形态
    def fix_esc(match):
        inner = match.group(1)
        args2 = re.findall(r'"(?:[^"\\]|\\.)*"', inner)
        if len(args2) >= 3:
            return match.group(0)
        gpos = match.start()
        ctx = data[max(0, gpos - 400):gpos + 400]
        color = "pink" if ctx.count("pink") > ctx.count("gold") else "gold"
        return '&lt;&lt;babyRentDisplay' + inner + ' "' + color + '"&gt;&gt;'

    data2 = re.sub(r'&lt;&lt;babyRentDisplay([^&]{0,200}?)&gt;&gt;', fix_esc, data)
    n2 = len(re.findall(r'&lt;&lt;babyRentDisplay', data)) - 0
    if data2 != data:
        open(HTML, "wb").write(data2.encode("utf-8"))
        print(f"✅ 已写回 {HTML}")
    else:
        print("⚠️ 转义形态未匹配，需手工处理")

# 校验
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n=== 校验 ===")
for m in re.finditer(r'<<babyRentDisplay([^>]{0,200})>>', g2):
    args = re.findall(r'"(?:[^"\\]|\\.)*"', m.group(1))
    print(f"  {len(args)} 参数: {m.group(0)[:100]!r}")
return_code = 0
sys.exit(return_code)
