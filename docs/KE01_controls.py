"""第 16-22 轮：交互控件绑定完整性。

16) <<button>> 里的宏是否闭合
17) <<radiobutton>> / <<checkbox>> 绑定的变量
18) <<numberStepper>> 的表达式
19) <<cycle>> / <<listbox>> 的 autoselect
20) 侧边栏 widget 引用
21) 设置页 toggle
22) 作弊菜单入口
"""
import html
import re
from collections import Counter

HTML = r"E:\TAML\_dol\work\index_modded6.html"
g = html.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))

print("=" * 94)
print("第 16 轮：<<button>> 配对")
print("=" * 94)
ob = len(re.findall(r"<<button\b", g))
cb = g.count("<</button>>")
print(f"  <<button>> {ob} / <</button>> {cb}  {'✅' if ob == cb else '❌ 差 ' + str(ob - cb)}")

print("\n" + "=" * 94)
print("第 17 轮：<<radiobutton>> / <<checkbox>> 绑定变量")
print("=" * 94)
for kind in ("radiobutton", "checkbox"):
    items = re.findall(r"<<" + kind + r'\s+"?([^\s>"]+)"?', g)
    print(f"  <<{kind}>>: {len(items)} 处")
    bad = []
    for v in items:
        vv = v.strip('"')
        if not vv.startswith("$") and not vv.startswith("_"):
            bad.append(vv)
    if bad:
        print(f"    可疑（不绑 $ 或 _）: {Counter(bad).most_common(8)}")

print("\n" + "=" * 94)
print("第 18 轮：<<numberStepper>> 表达式")
print("=" * 94)
ns = re.findall(r"<<numberStepper\s+([^\n>]{1,120})>>", g)
print(f"  <<numberStepper>>: {len(ns)} 处")
# 检查每个是否至少有一个反引号表达式或 $ 变量
bad_ns = [x for x in ns if "`" not in x and "$" not in x]
print(f"  无变量绑定的: {len(bad_ns)}")
for x in bad_ns[:8]:
    print(f"    {x[:100]!r}")

print("\n" + "=" * 94)
print("第 19 轮：<<cycle>> / <<listbox>> 的 autoselect")
print("=" * 94)
for kind in ("cycle", "listbox"):
    total = len(re.findall(r"<<" + kind + r"\b", g))
    auto = len(re.findall(r"<<" + kind + r'\s+[^\n>]*autoselect', g))
    print(f"  <<{kind}>> {total} 处，带 autoselect {auto} 处")

print("\n" + "=" * 94)
print("第 20 轮：侧边栏 widget")
print("=" * 94)
for w in ["sidebar", "updatesidebarimg", "updatesidebardescription", "sidebarLook"]:
    n = len(re.findall(r"<<" + w + r"\b", g))
    defined = bool(re.search(r'<<widget\s+"' + w + r'"', g))
    print(f"  {w:<28} 调用 {n:>5}  定义 {'✅' if defined else '❌'}")

print("\n" + "=" * 94)
print("第 21 轮：设置页 toggle")
print("=" * 94)
settings_widgets = re.findall(r'<<widget\s+"(settings[^"]*)"', g)
print(f"  settings* widget: {len(settings_widgets)} 个")
for w in settings_widgets[:12]:
    n = len(re.findall(r"<<" + re.escape(w) + r"\b", g))
    print(f"    {w:<32} 调用 {n}")

print("\n" + "=" * 94)
print("第 22 轮：作弊菜单入口")
print("=" * 94)
cheats = re.findall(r'<<widget\s+"(cheats[^"]*)"', g)
print(f"  cheats* widget: {len(cheats)} 个")
for w in cheats:
    n = len(re.findall(r"<<" + re.escape(w) + r"\b", g))
    flag = "✅" if n > 0 else "⚠️ 未被调用"
    print(f"    {w:<36} 调用 {n}  {flag}")
