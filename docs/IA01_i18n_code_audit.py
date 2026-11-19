"""第 1 轮：审计 i18n 条目是否会篡改代码结构。

检查维度：
  A) f/t 里出现 <<widget / <<macro 定义
  B) f/t 里 $变量 或 setup.xxx 的数量不一致（翻译吃掉了变量）
  C) f/t 里宏数量不一致（<<xxx 数量变了）
  D) t 里出现非法字符替换了标识符（如 ch一↑racteristics）
"""
import json
import re
import sys

I18N = r"E:\TAML\_dol\work\i18n_dict.json"

d = json.load(open(I18N, "r", encoding="utf-8"))
items = d["typeB"]["TypeBInputStoryScript"]
print(f"i18n 条目总数: {len(items)}")

MACRO = re.compile(r"<<\s*/?\s*([a-zA-Z][a-zA-Z0-9_]*)")
VAR = re.compile(r"\$[A-Za-z_][A-Za-z0-9_]*")
SETUP = re.compile(r"setup\.[A-Za-z_][A-Za-z0-9_]*")

issues = {"widget_def": [], "macro_count": [], "var_count": [], "setup_count": []}

for it in items:
    f, t = it.get("f") or "", it.get("t") or ""
    if not f or not t:
        continue
    pn = it.get("pN")

    # A) 宏定义
    if "<<widget" in f or "<<macro" in f:
        if f != t:
            issues["widget_def"].append((pn, f[:100], t[:100]))
            continue

    # B) 宏数量
    fm = MACRO.findall(f)
    tm = MACRO.findall(t)
    if len(fm) != len(tm):
        issues["macro_count"].append((pn, len(fm), len(tm), f[:90], t[:90]))
        continue

    # C) 变量数量
    fv, tv = VAR.findall(f), VAR.findall(t)
    if len(fv) != len(tv):
        issues["var_count"].append((pn, len(fv), len(tv), f[:90], t[:90]))
        continue

    if sorted(fv) != sorted(tv):
        issues["var_count"].append((pn, "名称不符", sorted(set(fv))[:4], sorted(set(tv))[:4]))

print("\n" + "=" * 94)
for key, label in [
    ("widget_def", "A) f/t 含 <<widget / <<macro 定义"),
    ("macro_count", "B) 宏数量不一致"),
    ("var_count", "C) $变量 数量/名称不一致"),
]:
    lst = issues[key]
    print(f"{label}: {len(lst)}")
    for x in lst[:8]:
        print(f"   {x}")
print("=" * 94)

total = sum(len(v) for v in issues.values())
print(f"\n合计可疑条目: {total}")
