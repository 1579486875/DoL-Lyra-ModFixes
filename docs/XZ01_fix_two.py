"""修最后两个检测误报：
  1) either() 要排除反引号字符串
  2) displayName 只报「纯 ASCII 且无 CJK」的
"""
import sys

REGRESS = r"E:\TAML\_dol\work\regress.py"
s = open(REGRESS, encoding="utf-8").read()

# ---- 1) either 加反引号处理 ----
OLD1 = """        base = re.sub(r'"(?:[^"\\\\]|\\\\.)*"', '""', inner)
        base = re.sub(r"'(?:[^'\\\\]|\\\\.)*'", "''", base)
        if "，" in base:"""
NEW1 = """        base = re.sub(r'"(?:[^"\\\\]|\\\\.)*"', '""', inner)
        base = re.sub(r"'(?:[^'\\\\]|\\\\.)*'", "''", base)
        base = re.sub(r"`(?:[^`\\\\]|\\\\.)*`", "``", base)
        if "，" in base:"""

if OLD1 in s:
    s = s.replace(OLD1, NEW1, 1)
    print("✅ either 检测已排除反引号字符串")
else:
    print("⚠️ 未找到 either 检测体")

# ---- 2) displayName 只报纯 ASCII ----
OLD2 = '''    en = re.findall(r'displayName:\\s*"([A-Za-z][^"]*)"', g)
    (ok if not en else bad)("[25] displayName 无纯英文", str(en[:3]))'''
NEW2 = '''    allDn = re.findall(r'displayName:\\s*"([^"]{1,60})"', g)
    en = [x for x in allDn if not CJK.search(x)]
    (ok if not en else bad)("[25] displayName 无纯英文", str(en[:3]))'''

if OLD2 in s:
    s = s.replace(OLD2, NEW2, 1)
    print("✅ displayName 检测只报纯 ASCII")
else:
    print("⚠️ 未找到 displayName 检测")

open(REGRESS, "w", encoding="utf-8").write(s)
print("\n完成")
