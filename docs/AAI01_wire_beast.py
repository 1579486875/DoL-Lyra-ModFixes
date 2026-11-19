"""把 setup 守卫修复加入 build_all，并查 beasttype 数据源。"""
import html
import re
import zipfile

BUILD = r"E:\TAML\_dol\work\build_all.py"
HTML = r"E:\TAML\_dol\work\index_modded6.html"

# 1) 加入 build_all（在 SF01/VL01 之后，必须每次都跑，因为它们是插入脚本）
s = open(BUILD, encoding="utf-8").read()
ANCHOR = '    (r"E:\\TAML\\_dol\\work\\ZO01_cn_macro_fix.py", "修中文宏名（<<保持了安静>> -> <<silently>>）"),'
NEW = (ANCHOR + '\n'
       '    (r"E:\\TAML\\_dol\\work\\AAD01_fix_setup_guard.py", "修 setup 守卫（SugarCube.setup 不存在）"),\n'
       '    (r"E:\\TAML\\_dol\\work\\AAE01_fix_selfassign.py", "删掉 var st = st 自赋值"),\n'
       '    (r"E:\\TAML\\_dol\\work\\AAH01_fix_all.py", "折叠 <<= 嵌套 + 修全角括号 + 英文单词"),')
if "AAD01_fix_setup_guard" not in s and ANCHOR in s:
    s = s.replace(ANCHOR, NEW, 1)
    open(BUILD, "w", encoding="utf-8").write(s)
    print("✅ 已加入 AAD01 / AAE01 / AAH01")
else:
    print("（已存在或未找到锚点）")

# 2) 查 beasttype
g = html.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n" + "=" * 88)
print("beasttype 的来源")
print("=" * 88)
for m in list(re.finditer(r"<<widget\s+\"beasttype\"\s*>>(.*?)<</widget>>", g, re.S))[:2]:
    print(f"  定义: {m.group(1)[:400]!r}")

print("\n  setup.beastTypes / beasttypes:")
for m in list(re.finditer(r"setup\.(beast\w*|Beast\w*)\s*(?:to|=)\s*", g))[:5]:
    print(f"    {g[max(0,m.start()-60):m.start()+300]!r}")

print("\n  beasttypes 数组:")
for m in list(re.finditer(r"beasttypes?\s*(?:to|=)\s*\[", g))[:3]:
    print(f"    {g[max(0,m.start()-80):m.start()+400]!r}")
