"""把 ZE01（CSS/变量名修复）和 ZJ02（babyRentDisplay 参数）加入 build_all。"""
P = r"E:\TAML\_dol\work\build_all.py"
s = open(P, encoding="utf-8").read()

OLD = '    (r"E:\\TAML\\_dol\\work\\TF01_nest_guard.py", "检查并修复 widget 嵌套（必须最后）"),'
NEW = ('    (r"E:\\TAML\\_dol\\work\\ZE01_fix_css_cn.py", "修 CSS 类名/变量名被翻译破坏"),\n'
       '    (r"E:\\TAML\\_dol\\work\\ZJ02_fix_babyrent.py", "补 babyRentDisplay 丢失的颜色参数"),\n'
       + OLD)

if "ZE01_fix_css_cn" not in s:
    if OLD in s:
        s = s.replace(OLD, NEW, 1)
        open(P, "w", encoding="utf-8").write(s)
        print("✅ 已加入 ZE01 / ZJ02")
    else:
        print("⚠️ 未找到 TF01 锚点")
else:
    print("（已存在）")
