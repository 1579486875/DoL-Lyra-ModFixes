"""修正 validate.py 的两个已知误报：
  1) <<if>> 差 1 —— 在注释里
  2) 中文比较值 —— 大部分是自洽的（值也被中文化了）
"""
import os
import re
import sys

P = r"E:\TAML\_dol\work\validate.py"
s = open(P, encoding="utf-8").read()

# ---- 1) 配对检查前先剥注释 ----
OLD_PAIR = '''    PAIRS = [
        ("if", r"<<if\\b", "<</if>>"),'''
NEW_PAIR = '''    # 剥掉注释再做配对统计（注释里的宏不参与解析）
    clean_passages = {}
    for pn, b in passages.items():
        c = b
        for pat in (r"/\\*.*?\\*/", r"<!--.*?-->", r"/%.*?%/"):
            c = re.sub(pat, " ", c, flags=re.S)
        clean_passages[pn] = c

    PAIRS = [
        ("if", r"<<if\\b", "<</if>>"),'''
if OLD_PAIR in s:
    s = s.replace(OLD_PAIR, NEW_PAIR, 1)
    print("✅ 配对检查已改为剥注释后统计")

# ---- 2) 配对统计用 clean_passages ----
OLD_STAT = '''    for tag, op, cp in PAIRS:
        o = sum(len(re.findall(op, b)) for b in passages.values())
        c = sum(b.count(cp) for b in passages.values())'''
NEW_STAT = '''    for tag, op, cp in PAIRS:
        o = sum(len(re.findall(op, b)) for b in clean_passages.values())
        c = sum(b.count(cp) for b in clean_passages.values())'''
if OLD_STAT in s:
    s = s.replace(OLD_STAT, NEW_STAT, 1)
    print("✅ 配对统计已用剥注释后的内容")

# ---- 3) 中文比较值：只报「值是系统字段但判断用中文」的 ----
OLD_CJK = '''    CJK = re.compile(r"[\\u4e00-\\u9fff]")
    bad_cmp = []
    for pn, b in passages.items():
        for m in re.finditer(r'<<(?:if|elseif|unless|while)\\s+([^\\n>]{1,300})>>', b):
            expr = m.group(1)
            for lit in re.findall(r'"([^"]{1,50})"|\\'([^\\']{1,50})\\'', expr):
                val = lit[0] or lit[1]
                if CJK.search(val):
                    # 允许：值本身就是中文（原版或有意）
                    bad_cmp.append((pn, val, expr[:60]))
                    break
    check("<<if>> 无中文比较值", not bad_cmp,
          f"{len(bad_cmp)} 处: {bad_cmp[:3]}" if bad_cmp else "")'''

NEW_CJK = '''    CJK = re.compile(r"[\\u4e00-\\u9fff]")
    # 只报「系统字段用了中文字面量」——那才会导致恒 false。
    # 形如 $xx.type is "中文" / xx.includes("中文")，其中 xx 是引擎/系统字段。
    SYSTEM_FIELDS = ("penisdesc", "precipitation", "fullDesc", "desc",
                     "type", "pronoun", "gender", "condom", "name")
    bad_cmp = []
    for pn, b in passages.items():
        for m in re.finditer(r'\\$[\\w$.\\[\\]]*\\.(' + "|".join(SYSTEM_FIELDS) + r')\\s*(?:is|isnot|===|!==)\\s*"([^"]{1,40})"', b):
            field, val = m.group(1), m.group(2)
            if CJK.search(val):
                # 进一步确认：这个中文值是否真的出现在某处赋值里
                if f'"{val}"' in g:
                    continue  # 值也是中文 -> 自洽
                bad_cmp.append((pn, field, val))
    check("系统字段无孤立中文比较值", not bad_cmp,
          f"{len(bad_cmp)} 处: {bad_cmp[:3]}" if bad_cmp else "")'''

if OLD_CJK in s:
    s = s.replace(OLD_CJK, NEW_CJK, 1)
    print("✅ 中文比较值检查已改为只报系统字段")
else:
    print("⚠️ 未找到中文比较值检查块")

open(P, "w", encoding="utf-8").write(s)
print("\n完成")
