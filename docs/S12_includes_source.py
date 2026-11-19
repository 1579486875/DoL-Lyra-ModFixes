"""轮12：.includes("中文") 的数据源追踪。

对每一处 X.includes("中文")：
  1. 找出 X 的赋值语句
  2. 判断赋值是中文还是英文
  3. 若赋值只有英文 -> 矛盾（includes 永远 false）
"""
import html
import re
import sys
import zipfile
from collections import Counter, defaultdict

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
CJK = re.compile(r"[\u4e00-\u9fff]")

z = zipfile.ZipFile(APK)
g = html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))

# 1) 收集所有 X.includes("值")
pattern = re.compile(r'([A-Za-z_$][\w.$\[\]"]*)\.includes\(\s*"([^"]*)"\s*\)')
hits = [(m.group(1), m.group(2), m.start()) for m in pattern.finditer(g)]
print(f".includes(...) 总数: {len(hits)}")

cn_hits = [(x, v, p) for x, v, p in hits if CJK.search(v)]
print(f"其中含中文的: {len(cn_hits)}")

# 2) 按「容器表达式」分组
by_expr = defaultdict(list)
for x, v, p in cn_hits:
    by_expr[x].append((v, p))

print(f"涉及 {len(by_expr)} 种容器表达式")

# 3) 对每个容器，找它的赋值来源
print("\n" + "=" * 90)
print("逐容器追踪")
print("=" * 90)

problems = []
for expr, vals in sorted(by_expr.items(), key=lambda kv: -len(kv[1])):
    # 只查带点/带下标的（简单变量太宽泛）
    if not (("." in expr) or ("[" in expr)):
        continue

    # 找赋值：expr = "..." 或 expr to "..."
    lits = set()
    for m in re.finditer(re.escape(expr) + r'\s*[:=]\s*"([^"]*)"', g):
        lits.add(m.group(1))
    # 也找 setup 表里的定义
    for m in re.finditer(r'"([^"]*)"[^"]*"[^"]*"', ""):
        pass

    cn_vals = [v for v, _ in vals]
    has_cn_lit = any(CJK.search(x) for x in lits)
    has_en_lit = any(re.match(r"^[A-Za-z]", x) for x in lits) if lits else False
    no_lit = not lits

    status = ""
    if no_lit:
        status = "⚪ 无直接字面值赋值（属性来自对象/表）"
    elif has_cn_lit:
        status = "✅ 赋值含中文"
    elif has_en_lit:
        status = "❌ 赋值只有英文"
        problems.append((expr, cn_vals[:3], sorted(lits)[:3]))
    print(f"\n  {expr}  (×{len(vals)})  {status}")
    print(f"    includes 中文: {cn_vals[:3]}")
    if lits:
        print(f"    赋值字面值: {sorted(lits)[:5]}")

print("\n" + "=" * 90)
print(f"结论：{len(problems)} 种容器的 includes 永远 false")
print("=" * 90)
for expr, vals, lits in problems:
    print(f"  ❌ {expr}.includes({vals[0]!r}) 但赋值只有 {lits}")

if not problems:
    print("  ✅ 无矛盾")

sys.exit(1 if problems else 0)
