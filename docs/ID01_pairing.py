"""第 7-12 轮：配对一致性审计（上一轮教训：改 A 不能打坏 B）。"""
import html
import re
from collections import Counter

HTML = r"E:\TAML\_dol\work\index_modded6.html"
g = html.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))

print("=" * 94)
print("第 7 轮：<<for _i>> 循环与中文数组的配对比")
print("=" * 94)
loops = Counter()
for m in re.finditer(r"<<for\s+(\w+)\s*=\s*0;\s*\1\s*<\s*([\w.\[\]$]+?)\.length", g):
    loops[(m.group(1), m.group(2))] += 1

for (var, arr), c in loops.most_common(25):
    cn = re.search(r"<<set " + re.escape(var) + r"cn\s*=\s*\[([^\]]*)\]>>", g)
    if not cn:
        continue
    items = [x for x in re.split(r'",\s*"', cn.group(1).strip(' "\t')) if x.strip()]
    # 该数组有几处定义/赋值
    print(f"  <<for {var}>> 循环 {c} 次   {arr}.length  vs  {var}cn[{len(items)}]")

print("\n" + "=" * 94)
print("第 8 轮：<<optionsfrom>> 参数定义检查")
print("=" * 94)
opts = Counter(x.strip() for x in re.findall(r"<<optionsfrom\s+([^\n>]{1,120})>>", g))
undef = []
for e, c in opts.most_common():
    m = re.match(r"^(?:setup\.)?(_?[A-Za-z_]\w*)$", e)
    if not m:
        continue
    name = m.group(1)
    pats = [
        r"<<set\s+" + re.escape(name) + r"\s+to",
        r"<<set\s+\$" + re.escape(name.lstrip("_")) + r"\s+to",
        r"<<set\s+setup\." + re.escape(name) + r"\s+to",
        r"setup\." + re.escape(name) + r"\s*=",
        r"\bV\." + re.escape(name) + r"\s*=",
    ]
    if not any(re.search(p, g) for p in pats):
        undef.append((e, c))
print(f"  <<optionsfrom>> 共 {sum(opts.values())} 处，静态找不到定义的 {len(undef)} 个")
for e, c in undef[:15]:
    print(f"    {c:>3}  {e!r}")

print("\n" + "=" * 94)
print("第 9 轮：setup.* 被引用 Top 20（定义缺失标红）")
print("=" * 94)
for name, c in Counter(re.findall(r"setup\.([A-Za-z_]\w*)", g)).most_common(20):
    defined = bool(re.search(r"<<set\s+setup\." + re.escape(name) + r"\s+to", g)) or \
              bool(re.search(r"setup\." + re.escape(name) + r"\s*=", g))
    print(f"  {c:>4}  setup.{name:<30} {'✅' if defined else '❌'}")

print("\n" + "=" * 94)
print("第 10 轮：<<cycle>> 绑定")
print("=" * 94)
for it, c in Counter(x.strip() for x in re.findall(r"<<cycle\s+([^\n>]{1,80})>>", g)).most_common(10):
    print(f"  {c:>3}  {it!r}")

print("\n" + "=" * 94)
print("第 11 轮：硬编码中文数组（可能与其他数据错配）")
print("=" * 94)
hard = re.findall(r"<<set (\w+cn)\s*=\s*\[([^\]]{0,400})\]>>", g)
print(f"  共 {len(hard)} 个")
for name, body in hard[:15]:
    cnt = len([x for x in re.split(r'",\s*"', body.strip(' "\t')) if x.strip()])
    # 对应的非 cn 版本
    base = name[:-2]
    base_defined = bool(re.search(r"<<set\s+" + re.escape(base) + r"\s+to", g))
    print(f"    {name}: {cnt} 项   （{base} {'有' if base_defined else '无'}静态定义）")

print("\n" + "=" * 94)
print("第 12 轮：<<if xxx.>> 里的裸变量（可能丢 $）")
print("=" * 94)
susp = []
for m in re.finditer(r"<<(?:if|elseif)\s+([a-z][a-zA-Z0-9_]*)\.[a-zA-Z_]", g):
    name = m.group(1)
    if re.search(r"\$" + re.escape(name) + r"\b", g):
        susp.append((name, g[max(0, m.start() - 50):m.start() + 90]))
print(f"  可疑 {len(susp)} 处")
for name, ctx in susp[:10]:
    print(f"    {name}: {ctx!r}")
