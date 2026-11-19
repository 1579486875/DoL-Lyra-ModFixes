"""把 XC01_collapse 从中间位置移到 build_all 的最末尾（TF01 之前）。"""
import re

P = r"E:\TAML\_dol\work\build_all.py"
s = open(P, encoding="utf-8").read()

LINE = '    (r"E:\\TAML\\_dol\\work\\XC01_collapse.py", "折叠多层宏嵌套（每次烤入都会多包一层）"),\n'

if LINE not in s:
    print("❌ 未找到 XC01 行")
    raise SystemExit(1)

# 删除原位置
s = s.replace(LINE, "", 1)

# 插到 TF01 之前（那是最后一步）
OLD_TF = '    (r"E:\\TAML\\_dol\\work\\TF01_nest_guard.py", "检查并修复 widget 嵌套"),'
NEW_TF = LINE + '    (r"E:\\TAML\\_dol\\work\\TF01_nest_guard.py", "检查并修复 widget 嵌套（必须最后）"),'

if OLD_TF in s:
    s = s.replace(OLD_TF, NEW_TF, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("✅ XC01 已移到末尾（TF01 之前）")
else:
    print("⚠️ 未找到 TF01")

# 显示顺序
print("\n当前脚本顺序（末尾 6 个）：")
for line in s.split("\n"):
    if "_dol\\\\work\\\\" in line and ".py" in line:
        m = re.search(r"work\\\\([\w\d]+_?\w*)\.py", line)
        if m:
            print(f"  {m.group(1)}")
