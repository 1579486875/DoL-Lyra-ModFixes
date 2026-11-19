"""修 AAJ01 的拼接 bug（漏了 | 分隔符），并清理已产生的粘连。"""
import re

P = r"E:\TAML\_dol\work\AAJ01_fix_table.py"
s = open(P, encoding="utf-8").read()

# 修拼接：table + "|".join(need)  ->  table + "|" + "|".join(need)
OLD = 'new_table = table + "|".join(need)'
NEW = 'new_table = table.rstrip("|") + "|" + "|".join(need)'
if OLD in s:
    s = s.replace(OLD, NEW, 1)
    print("✅ 已修拼接分隔符")
else:
    print("⚠️ 未找到拼接语句")

# 增加：清理已粘连的形态（防止上一次的污染残留）
CLEAN = '''
# 清理历史上的粘连（table 末尾直接接 eels 等）
import re as _re
new_table = _re.sub(r"([^|])(eels|whales|lizards|slimes|worms),(?=\\S)", r"\\1|\\2,", new_table)
'''
if "清理历史上的粘连" not in s:
    anchor = 'if need:'
    if anchor in s:
        s = s.replace(anchor, CLEAN + "\n" + anchor, 1)
        print("✅ 已加粘连清理")

open(P, "w", encoding="utf-8").write(s)
print("\n完成")
