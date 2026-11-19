"""补最后 3 个 displayName，并入 XK01。"""
import re

XK = r"E:\TAML\_dol\work\XK01_more_dn.py"
s = open(XK, encoding="utf-8").read()

EXTRA = '''    "Crop yield:": "作物产量：",
    "Dildos:": "假阳具：",
    "Divine Transformations:": "神圣转化：",
    "Freckles:": "雀斑：",
    "Natural Skintone:": "自然肤色：",
    "Cost of lewd clothes:": "淫秽衣物价格：",
    "Cost of school clothes:": "校服价格：",
    "Cost of underwear:": "内衣价格：",
    "Starting season:": "起始季节：",
    "Game difficulty:": "游戏难度：",
    "Ironman mode:": "铁人模式：",
'''

if "Crop yield:" not in s:
    anchor = '    "Combat:": "战斗：",'
    if anchor in s:
        s = s.replace(anchor, EXTRA + anchor, 1)
        open(XK, "w", encoding="utf-8").write(s)
        print("✅ 已补最后 3 个 displayName")
    else:
        print("⚠️ 未找到锚点")
else:
    print("（已存在）")
