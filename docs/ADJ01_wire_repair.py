"""把 ADI01 加入 build_all，并让 validate/regress 允许 Widgets Repair passage。"""
import re

BUILD = r"E:\TAML\_dol\work\build_all.py"
VALID = r"E:\TAML\_dol\work\validate.py"
REG = r"E:\TAML\_dol\work\regress.py"

# 1) build_all
s = open(BUILD, encoding="utf-8").read()
ANCHOR = '    (r"E:\\TAML\\_dol\\work\\AAP01_final_table.py", "最终修复 NPCTypeList 粘连+补复数"),'
NEW = (ANCHOR + '\n'
       '    (r"E:\\TAML\\_dol\\work\\ADI01_safe_passage.py", "新建 Widgets Repair passage 承载注册失败的 widget"),')
if "ADI01_safe_passage" not in s and ANCHOR in s:
    s = s.replace(ANCHOR, NEW, 1)
    open(BUILD, "w", encoding="utf-8").write(s)
    print("✅ 已加入 ADI01")
else:
    print("（build_all 已存在或未找到）")

# 2) validate.py 允许额外 passage
v = open(VALID, encoding="utf-8").read()
OLD = '''        mp = set(passages.keys())
        check(f"passage 集合一致（{len(mp)} / {len(vp)}）", mp == vp,
              f"多出 {len(mp-vp)}，缺少 {len(vp-mp)}")'''
NEW2 = '''        mp = set(passages.keys())
        # 允许我们新增的修复 passage
        ALLOW_EXTRA = {"Widgets Repair"}
        extra = mp - vp - ALLOW_EXTRA
        lack = vp - mp
        check(f"passage 集合一致（{len(mp)} / {len(vp)}）", not extra and not lack,
              f"多出 {len(extra)} {sorted(extra)[:3]}，缺少 {len(lack)} {sorted(lack)[:3]}")'''
if OLD in v:
    v = v.replace(OLD, NEW2, 1)
    open(VALID, "w", encoding="utf-8").write(v)
    print("✅ validate.py 已允许 Widgets Repair")
else:
    print("⚠️ validate.py 未找到 passage 集合检查")

# 3) regress.py 同理
r = open(REG, encoding="utf-8").read()
OLD3 = '''        check(f"passage 集合一致（{len(mp)} / {len(vp)}）", mp == vp,
              f"多出 {len(mp-vp)}，缺少 {len(vp-mp)}")'''
NEW3 = '''        ALLOW_EXTRA = {"Widgets Repair"}
        extra = mp - vp - ALLOW_EXTRA
        lack = vp - mp
        check(f"passage 集合一致（{len(mp)} / {len(vp)}）", not extra and not lack,
              f"多出 {len(extra)}，缺少 {len(lack)}")'''
if OLD3 in r:
    r = r.replace(OLD3, NEW3, 1)
    open(REG, "w", encoding="utf-8").write(r)
    print("✅ regress.py 已允许 Widgets Repair")
else:
    print("（regress.py 无需改或未找到）")
