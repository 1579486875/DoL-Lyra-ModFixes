"""把 AAJ01（补复数映射）加入 build_all，放在 AD_direct_patch 之后。"""
P = r"E:\TAML\_dol\work\build_all.py"
s = open(P, encoding="utf-8").read()

ANCHOR = '    (r"E:\\TAML\\_dol\\work\\AD_direct_patch.py", "直接注入：5 张映射表 / 关系值名 / 状态名 / 脸型键"),'
NEW = (ANCHOR + '\n'
       '    (r"E:\\TAML\\_dol\\work\\AAJ01_fix_table.py", "补 NPCTypeList 的复数形式（eels/whales/lizards）"),')

if "AAJ01_fix_table" not in s and ANCHOR in s:
    s = s.replace(ANCHOR, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("✅ 已加入 AAJ01")
else:
    print("（已存在或未找到锚点）")
