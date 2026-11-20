"""T20：扫 setup.clothes 里缺 cn_name / cn_name_cap 的服装。

玩家看到英文衣服名的根因通常是：
  - 服装对象没有 cn_name_cap 字段
  - 或 cn_name_cap 的值就是英文
"""
import html as H
import json
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

# DoL 的服装数据是在 <<script>> 里用 setup.clothes.xxx = [...] 定义的
# 但实际运行时是 initXxx() 函数里 push 的。静态扫描不可靠。
#
# 这里改用另一种判据：找所有 cn_name 赋值，统计覆盖率。

print("=" * 95)
print("1. cn_name / cn_name_cap 的出现次数")
print("=" * 95)
for k in ("cn_name", "cn_name_cap", "name_cap"):
    print(f"  {k}: {g.count(k)}")

print("\n" + "=" * 95)
print("2. 找 cn_name 的数据源（字典/映射）")
print("=" * 95)
# 常见形态：{ "英文名": "中文名", ... }
for pat, label in (
    (r'var\s+\w*[Cc][Nn]\w*\s*=\s*\{', "var *CN* = {"),
    (r'setup\.\w*[Cc][Nn]\w*\s*=\s*\{', "setup.*CN* = {"),
    (r'"[^"]{3,40}"\s*:\s*"[^"]{1,30}"(?=[,}])', None),
):
    if label:
        hs = list(re.finditer(pat, g))
        print(f"  {label}: {len(hs)}")
        for h in hs[:5]:
            print(f"    @{h.start()}: {g[h.start():h.start()+200]!r}")

print("\n" + "=" * 95)
print("3. 初始化函数里的 cn_name 赋值形态")
print("=" * 95)
# 找 initUpper 等函数里的对象定义
for fn in ("initUpper", "initLower", "initUnderUpper", "initHandheld"):
    m = re.search(r"function " + fn + r"\s*\(\)\s*\{", g)
    if not m:
        continue
    seg = g[m.start():m.start() + 3000]
    has_cn = "cn_name" in seg
    print(f"  {fn}: cn_name 出现 {seg.count('cn_name')} 次")
    if has_cn:
        mm = re.search(r"cn_name[^,\n]{0,80}", seg)
        print(f"    样例: {mm.group(0)!r}")

print("\n" + "=" * 95)
print("4. 全库找「英文 name + 无 cn_name」的衣服定义")
print("=" * 95)
# 形态：{ name: "xxx", ... } 里没有 cn_name
n_objs = 0
n_no_cn = 0
samples = []
for m in re.finditer(r'\{\s*name:\s*"([^"]{3,50})"[^}]{0,800}\}', g):
    body = m.group(0)
    n_objs += 1
    if "cn_name" not in body:
        n_no_cn += 1
        if len(samples) < 15:
            samples.append(m.group(1))

print(f"  含 name: 的对象: {n_objs}")
print(f"  其中无 cn_name  : {n_no_cn}")
print(f"  样例（前 15）:")
for s in samples:
    print(f"    {s!r}")
