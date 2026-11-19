"""把 XJ01/XK01 加入 build_all（在 PE01 之后）。"""
import os

P = r"E:\TAML\_dol\work\build_all.py"
s = open(P, encoding="utf-8").read()

OLD = '''    (r"E:\\TAML\\_dol\\work\\PK01_headers_cn.py", "替换 settingsHeader 里的英文标题"),'''
NEW = '''    (r"E:\\TAML\\_dol\\work\\PK01_headers_cn.py", "替换 settingsHeader 里的英文标题"),
    (r"E:\\TAML\\_dol\\work\\XJ01_dn_full.py", "翻 displayName（短标签，UB01 会跳过）"),
    (r"E:\\TAML\\_dol\\work\\XK01_more_dn.py", "补第二批 displayName"),'''

if OLD in s and "XJ01_dn_full" not in s:
    s = s.replace(OLD, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("✅ 已加入 XJ01 / XK01")
else:
    print("（已存在或未找到）")
