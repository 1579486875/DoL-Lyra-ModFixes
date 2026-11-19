"""第 25-30 轮：正则回溯 / 循环风险 / 性能热点。

25) 灾难性回溯正则（嵌套量词）
26) <<for>> 循环的终点是否可能无限
27) 超大 passage（可能卡顿）
28) 深拷贝 / 递归
29) 全局符号冲突
30) 总结
"""
import html
import re
from collections import Counter

MODDED = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(MODDED, "rb").read().decode("utf-8", "replace")
g = html.unescape(raw)

print("=" * 94)
print("第 25 轮：灾难性回溯正则")
print("=" * 94)
# 找 JS 里的正则字面量，检查嵌套量词
risky = []
for m in re.finditer(r"/((?:[^/\\\n]|\\.)+)/([gimsuy]*)", g):
    pat = m.group(1)
    # 嵌套量词：(a+)+ / (a*)* / (a|a)+
    if re.search(r"\([^)]*[+*][^)]*\)[+*]", pat):
        risky.append(pat)
    # 多个 .* 相邻
    elif pat.count(".*") >= 3:
        risky.append(pat)
print(f"  可疑正则: {len(risky)}")
for p in Counter(risky).most_common(10):
    print(f"    {p[1]:>3}  /{p[0][:80]}/")

print("\n" + "=" * 94)
print("第 26 轮：<<for>> 循环安全性")
print("=" * 94)


def extract_macros(text, pat):
    out = []
    for m in re.finditer(pat, text):
        i = m.end()
        depth = 1
        while i < len(text) and depth > 0:
            if text.startswith("<<", i):
                depth += 1
                i += 2
            elif text.startswith(">>", i):
                depth -= 1
                i += 2
            else:
                i += 1
        out.append(text[m.end():i - 2].strip())
    return out


fors = extract_macros(g, r"<<for\b")
print(f"  <<for>> 共 {len(fors)} 处")
# 检查是否有「无步进」或「条件恒真」的
suspicious = []
for f in fors:
    if not f:
        continue
    # 分号分隔的三段式
    if ";" in f:
        parts = [x.strip() for x in f.split(";")]
        if len(parts) == 3:
            cond, step = parts[1], parts[2]
            var = parts[0].split("=")[0].strip()
            # 步进里没提到循环变量
            if var and var not in step:
                suspicious.append(f[:100])
print(f"  步进可疑: {len(suspicious)}")
for s in suspicious[:8]:
    print(f"    {s!r}")

print("\n" + "=" * 94)
print("第 27 轮：超大 passage（>200KB，可能卡顿）")
print("=" * 94)
sizes = []
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
    pn = html.unescape(m.group(1))
    sizes.append((pn, len(m.group(2))))
sizes.sort(key=lambda x: -x[1])
print(f"  passage 总数 {len(sizes)}，总字节 {sum(s for _, s in sizes):,}")
for pn, s in sizes[:12]:
    print(f"    {s:>9,}  {pn}")

print("\n" + "=" * 94)
print("第 28 轮：深拷贝 / 递归")
print("=" * 94)
for kw in ("clone(", "deepMerge", "JSON.parse(JSON.stringify", "structuredClone", "Object.assign"):
    print(f"  {kw:<28} {len(re.findall(re.escape(kw), g)):>5} 处")

print("\n" + "=" * 94)
print("第 29 轮：全局符号冲突（window.xxx = 赋值）")
print("=" * 94)
assigns = re.findall(r"window\.([A-Za-z_]\w*)\s*=(?!=)", g)
c = Counter(assigns)
print(f"  window.* 赋值: {len(c)} 种")
# 找重复赋值（可能冲突）
dup = {k: v for k, v in c.items() if v > 1}
print(f"  多次赋值（可能冲突）: {len(dup)}")
for k, v in sorted(dup.items(), key=lambda x: -x[1])[:12]:
    print(f"    {v:>3}  window.{k}")

print("\n" + "=" * 94)
print("第 30 轮：总结")
print("=" * 94)
print(f"  正则回溯风险: {len(risky)}")
print(f"  循环步进可疑: {len(suspicious)}")
print(f"  超大 passage: {len([1 for _, s in sizes if s > 200000])}")
print(f"  window 重复赋值: {len(dup)}")
