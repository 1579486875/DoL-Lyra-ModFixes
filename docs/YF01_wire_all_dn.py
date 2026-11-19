"""把 YE02_all_dn 加入 build_all（放在 XK01 之后）。"""
P = r"E:\TAML\_dol\work\build_all.py"
s = open(P, encoding="utf-8").read()

OLD = '    (r"E:\\TAML\\_dol\\work\\XK01_more_dn.py", "补第二批 displayName"),'
NEW = (OLD + '\n'
       '    (r"E:\\TAML\\_dol\\work\\YE02_all_dn.py", "一次性翻完剩余 103 个 displayName"),')

if OLD in s and "YE02_all_dn" not in s:
    s = s.replace(OLD, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("✅ 已加入 YE02_all_dn")
else:
    print("（已存在或未找到）")
