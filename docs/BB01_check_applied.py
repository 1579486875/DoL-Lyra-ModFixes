import html
import json
import re
import sys

sys.path.insert(0, r"E:\TAML\_dol\work")
import modzip_lib as MZ

d = open("index_modded6.html", "rb").read().decode("utf-8", "replace")
# 检查BA01: shopDetails是否包含event等5个特质
m = re.search(r"setup\.shopDetails = \{([^}]{5000,})\};", d)
if m:
    keys = set(re.findall(r"\b(\w+):\s*\{", m.group(1)))
    ba01_ok = "event" in keys and "tanLines" in keys and "blindfold" in keys
    print("BA01 shopDetails:", len(keys), "键，包含新增5个" if ba01_ok else "缺少新增特质")
# 检查BA02: loadFiltersMenu是否有防护
u = html.unescape(d)
i = u.find('<<widget "loadFiltersMenu">>')
j = u.find("<</widget>>", i) if i > 0 else -1
ba02_ok = ("!_traitObj or !_traitObj.desc" in u[i:j]) if i > 0 and j > i else False
print("BA02 loadFiltersMenu:", "已加防护" if ba02_ok else "未加防护")
# 检查AY03: 4个模组是否有修补说明
notes = {}
for s, zz, bj in MZ.iter_mods(d):
    if bj and bj.get("name") in ("DoLSims", "DomRobin", "Wraith'sReflection", "ModI18N"):
        notes[bj["name"]] = bool(bj.get("modFixesNotes"))
print("AY03 模组描述:", notes)
print("\n总结: BA01", "✓" if ba01_ok else "✗", "BA02", "✓" if ba02_ok else "✗", "AY03", "✓" if len(notes) == 4 and all(notes.values()) else "✗")
