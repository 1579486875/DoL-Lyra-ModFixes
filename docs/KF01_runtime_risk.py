"""第 23-30 轮：运行时错误风险扫描。

23) `.length` / `.includes` / `.forEach` 作用在可能 undefined 的表达式上
24) <<= expr>> 可能返回 undefined 的
25) 除零 / Math 边界
26) JSON.parse / JSON.stringify
27) 数组索引越界
28) 可选链缺失
29) 递归/深拷贝风险
30) 最终回归
"""
import html
import re
from collections import Counter

HTML = r"E:\TAML\_dol\work\index_modded6.html"
g = html.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))

print("=" * 94)
print("第 23 轮：<<if X.length>> 类断言（X 可能是 undefined）")
print("=" * 94)
risky = []
for m in re.finditer(r"<<(?:if|elseif)\s+([^\n>]{1,120}?)>>", g):
    expr = m.group(1)
    if ".length" not in expr and ".includes" not in expr:
        continue
    # 判断是否对裸 setup.xxx 或 $xxx 直接取 length（无 ?? / || / typeof 保护）
    if re.search(r"(?:setup\.\w+|\$\w+)\s*\.length", expr) and \
       not re.search(r"\?\?|\|\||typeof", expr):
        risky.append(expr[:100])
c = Counter(risky)
print(f"  可疑 {len(c)} 种 / {sum(c.values())} 处")
for e, n in c.most_common(12):
    print(f"    {n:>3}  {e!r}")

print("\n" + "=" * 94)
print("第 24 轮：<<= expr>> 可能返回 undefined")
print("=" * 94)
outs = Counter(re.findall(r"<<=\s*([^\n>]{1,120}?)>>", g))
print(f"  <<=>> 共 {sum(outs.values())} 处")
# 找没有 ?? / || / ternary 的简单属性访问
simple = [(e, n) for e, n in outs.items()
          if re.fullmatch(r"\s*[\w.]+\s*", e) and "?" not in e and "|" not in e]
print(f"  纯属性直出（可能 undefined）: {len(simple)}")
for e, n in simple[:12]:
    print(f"    {n:>3}  {e!r}")

print("\n" + "=" * 94)
print("第 25 轮：除零 / Math 边界")
print("=" * 94)
div = re.findall(r"Math\.(?:round|floor|ceil)\s*\([^)]*/\s*([A-Za-z_$][\w.$\[\]]*)", g)
print(f"  Math.x(a/b) 形式: {len(div)}")
for d in Counter(div).most_common(8):
    print(f"    {d[1]:>3}  除以 {d[0]}")

print("\n" + "=" * 94)
print("第 26 轮：JSON.parse 无 try/catch")
print("=" * 94)
jp = re.findall(r"JSON\.parse\s*\(", g)
print(f"  JSON.parse: {len(jp)} 处（SugarCube 内部多数有保护）")

print("\n" + "=" * 94)
print("第 27 轮：数组索引越界风险")
print("=" * 94)
idx = re.findall(r"\$\w+\[[^\]]{1,40}\]\.\w+", g)
print(f"  $arr[i].prop 形式: {len(idx)} 处")
for e, n in Counter(idx).most_common(8):
    print(f"    {n:>3}  {e}")

print("\n" + "=" * 94)
print("第 28 轮：可选链使用情况")
print("=" * 94)
opt = len(re.findall(r"\?\.[A-Za-z_]", g))
print(f"  可选链 ?. 使用: {opt} 处（越多越安全）")

print("\n" + "=" * 94)
print("第 29 轮：deepMerge / clone 深拷贝")
print("=" * 94)
for kw in ("deepMerge", "clone(", "Object.assign", "structuredClone"):
    print(f"  {kw:<20} {len(re.findall(re.escape(kw), g)):>5} 处")

print("\n" + "=" * 94)
print("第 30 轮：最终回归（与 vanilla 对照）")
print("=" * 94)


def load(apk):
    import zipfile
    z = zipfile.ZipFile(apk)
    r = z.read("assets/www/index.html").decode("utf-8", "replace")
    out = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', r, re.S):
        out[html.unescape(m.group(1))] = html.unescape(m.group(2))
    return out


vb = load(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk")
mb = load(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
print(f"  passage: vanilla {len(vb)}  modded {len(mb)}  {'✅' if set(vb) == set(mb) else '❌'}")
for tag, op, cp in [("if", r"<<if\b", "<</if>>"), ("for", r"<<for\b", "<</for>>"),
                    ("switch", r"<<switch\b", "<</switch>>"), ("link", r"<<link\b", "<</link>>"),
                    ("button", r"<<button\b", "<</button>>")]:
    vo = sum(len(re.findall(op, b)) for b in vb.values())
    vc = sum(b.count(cp) for b in vb.values())
    mo = sum(len(re.findall(op, b)) for b in mb.values())
    mc = sum(b.count(cp) for b in mb.values())
    print(f"  {tag:<8} vanilla {vo}/{vc}  modded {mo}/{mc}  {'✅' if mo == mc and vo == vc else '⚠️'}")
