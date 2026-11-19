"""把 ZO01 加入 build_all，并把「中文宏名」检测加入 validate.py。"""
import re

BUILD = r"E:\TAML\_dol\work\build_all.py"
VALID = r"E:\TAML\_dol\work\validate.py"

# 1) build_all
s = open(BUILD, encoding="utf-8").read()
OLD = '    (r"E:\\TAML\\_dol\\work\\ZE01_fix_css_cn.py", "修 CSS 类名/变量名被翻译破坏"),'
NEW = (OLD + '\n'
       '    (r"E:\\TAML\\_dol\\work\\ZO01_cn_macro_fix.py", "修中文宏名（<<保持了安静>> -> <<silently>>）"),')
if OLD in s and "ZO01_cn_macro_fix" not in s:
    s = s.replace(OLD, NEW, 1)
    open(BUILD, "w", encoding="utf-8").write(s)
    print("✅ ZO01 已加入 build_all")
else:
    print("（build_all 已存在或未找到）")

# 2) validate.py 加检测（在文件体积检查之前插入）
v = open(VALID, encoding="utf-8").read()
ANCHOR = '''    print("\\n" + "=" * 90)
    print("10) 文件体积")'''
NEW_CHECK = '''    print("\\n" + "=" * 90)
    print("9b) 中文宏名（<<中文>> 是非法宏）")
    print("=" * 90)
    cn_macros = re.findall(r"<<([\\u4e00-\\u9fff][^>]{0,60})>>", g)
    check(f"无中文宏名", not cn_macros, str(cn_macros[:5]))

    print("\\n" + "=" * 90)
    print("9c) 属性表达式（@xxx）里含中文")
    print("=" * 90)
    attr_cn = []
    for m in re.finditer(r'@([\\w:-]+)="([^"]{0,400})"', g):
        expr = m.group(2)
        if not re.search(r"[\\u4e00-\\u9fff]", expr):
            continue
        base = re.sub(r'"(?:[^"\\\\]|\\\\.)*"', '""', expr)
        base = re.sub(r"'(?:[^'\\\\]|\\\\.)*'", "''", base)
        if re.search(r"[\\u4e00-\\u9fff]", base):
            attr_cn.append((m.group(1), expr[:60]))
    check("属性表达式无裸中文", not attr_cn, str(attr_cn[:3]))

    print("\\n" + "=" * 90)
    print("10) 文件体积")'''

if ANCHOR in v and "9b) 中文宏名" not in v:
    v = v.replace(ANCHOR, NEW_CHECK, 1)
    open(VALID, "w", encoding="utf-8").write(v)
    print("✅ validate.py 已加 2 项新检测")
else:
    print("（validate.py 已存在或未找到锚点）")
