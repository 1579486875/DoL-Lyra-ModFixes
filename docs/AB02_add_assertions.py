"""AB02：给回归套件加 2 条新断言。

1. C.no_args_leak      —— 正文里的 _args[N] 泄漏（第 6 轮修了 14 处，但没断言）
2. C.no_double_escape  —— 双重转义 &amp;lt; / &amp;gt;（第 6 轮修了 21 处，但没断言）

判据必须排除：
  - HTML 属性里（@onclick="..."）
  - HTML 注释里（<!-- -->）
  - JS 注释里（/* */）
  - <<set>> / <<run>> 里（在宏内）
"""
import ast
import re

P = r"E:\TAML\_dol\work\REGRESS_ALL.py"
s = open(P, encoding="utf-8").read()

if "no_args_leak" in s:
    print("（已存在，跳过）")
    raise SystemExit(0)

# 锚点：C 组的最后一条
ANCHOR = 'chk("C", "no_macro_in_if", n_macro_in_if == 0, f"{n_macro_in_if} 处")\n'
if ANCHOR not in s:
    print("MISS 找不到锚点")
    raise SystemExit(1)

NEW = '''chk("C", "no_macro_in_if", n_macro_in_if == 0, f"{n_macro_in_if} 处")

# ★ _args[N] 泄漏到正文（SugarCube 不会自动求值 _args，会输出字面）
def _scan_args_leak(text):
    cnt = 0
    for m in re.finditer(r"_args\\[(\\d+)\\]", text):
        pos = m.start()
        pre = text[max(0, pos - 600):pos]
        # 在宏里
        if pre.rfind("<<") > pre.rfind(">>"):
            continue
        # HTML 注释
        if text.rfind("<!--", 0, pos) > text.rfind("-->", 0, pos):
            continue
        # JS 注释
        if text.rfind("/*", 0, pos) > text.rfind("*/", 0, pos):
            continue
        # 前后要有中文（说明在正文）
        ctx = text[max(0, pos - 40):pos + 50]
        if not re.search(r"[\\u4e00-\\u9fff]", ctx):
            continue
        # HTML 属性里
        lt = pre.rfind("<")
        gt = pre.rfind(">")
        if lt > gt:
            seg = pre[lt:]
            if '"' in seg or "'" in seg:
                continue
        # <<set ... >> 里（内含 "<<" 字符串会让宏判据失效）
        if re.search(r"<<set\\s+[^\\n]{0,400}$", pre):
            continue
        cnt += 1
    return cnt

n_args_leak = _scan_args_leak(g)
chk("C", "no_args_leak", n_args_leak == 0, f"{n_args_leak} 处")

# ★ 双重转义 &amp;lt; / &amp;gt;
n_amp_lt = raw.count("&amp;lt;")
n_amp_gt = raw.count("&amp;gt;")
chk("C", "no_double_escape", n_amp_lt == 0 and n_amp_gt == 0,
    f"&amp;lt;={n_amp_lt} &amp;gt;={n_amp_gt}")
'''

s = s.replace(ANCHOR, NEW, 1)
open(P, "w", encoding="utf-8").write(s)
ast.parse(open(P, encoding="utf-8").read())
print("✅ 已加 2 条断言")
print("   C.no_args_leak")
print("   C.no_double_escape")
