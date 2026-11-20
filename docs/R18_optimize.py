"""R18：优化 no_macro_in_if 断言（不逐字符扫 100MB）。

思路：<<if>> 表达式几乎从不跨行（跨行的只有个别排版），
      所以只在「同一行」内找配对的 >> 即可，速度提升几百倍。
"""
import ast
import re

P = r"E:\TAML\_dol\work\REGRESS_ALL.py"
s = open(P, encoding="utf-8").read()

start = s.find("# ★ 宏调用不能出现在 <<if>> 表达式里")
if start < 0:
    print("MISS")
    raise SystemExit(1)
end = s.find('chk("C", "no_macro_in_if"')
end = s.find("\n", end) + 1

NEW = '''# ★ 宏调用不能出现在 <<if>> 表达式里（社交界面崩溃的根因）
# 判据：按行扫描，取 <<if/<<elseif 到本行最近的 >> 之间的内容，挖掉字符串后看还有没有 <<宏名
def _scan_if_macro(text):
    cnt = 0
    for line in text.split("\\n"):
        if "<<if" not in line and "<<elseif" not in line:
            continue
        for m2 in re.finditer(r"<<(?:if|elseif)\\b", line):
            rest = line[m2.end():]
            e = rest.find(">>")
            body = rest if e < 0 else rest[:e]
            b2 = re.sub(r'"[^"]*"', lambda x: " " * len(x.group(0)), body)
            b2 = re.sub(r"'[^']*'", lambda x: " " * len(x.group(0)), b2)
            b2 = re.sub(TICK + "[^" + TICK + "]*" + TICK, lambda x: " " * len(x.group(0)), b2)
            if re.search(r"<<[A-Za-z]", b2):
                cnt += 1
    return cnt

n_macro_in_if = _scan_if_macro(g)
chk("C", "no_macro_in_if", n_macro_in_if == 0, f"{n_macro_in_if} 处")
'''

s = s[:start] + NEW + s[end:]
open(P, "w", encoding="utf-8").write(s)
ast.parse(open(P, encoding="utf-8").read())
print("OK 已优化")
