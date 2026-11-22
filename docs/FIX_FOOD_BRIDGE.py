# -*- coding: utf-8 -*-
"""给 More-Useful-Foodstuff 的 eat() 加 BasicNeeds 联动（饥饿/口渴），重打包并写回 index。"""
import base64
import io
import json
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
SRC = r"E:\TAML\_dol\work\_downloads\More-Useful-Foodstuff-v0.2.60.mod.zip"

ANCHOR = "        vars[INTAKE_KEY] = [...check.intake.active, {time:check.intake.now,cost:check.cost,id}];\n        const after = snapshot(vars);"
BRIDGE = ("        vars[INTAKE_KEY] = [...check.intake.active, {time:check.intake.now,cost:check.cost,id}];\n"
          "        // [DoL-Lyra-ModFixes] 与 BasicNeeds 联动：进食补饥饿/解渴\n"
          "        try {\n"
          "            const _bn = window.BN && window.BN.ensureVars ? window.BN.ensureVars() : null;\n"
          "            if (_bn) {\n"
          "                const _cost = Number(check.cost) || 15;\n"
          "                _bn.hunger = Math.max(0, (_bn.hunger || 0) - _cost * 80);\n"
          "                _bn.thirst = Math.max(0, (_bn.thirst || 0) - _cost * 30);\n"
          "                if (window.BN.updatePanel) window.BN.updatePanel();\n"
          "            }\n"
          "        } catch (e) { console.warn('[FoodEffects] BasicNeeds 联动失败', e); }\n"
          "        const after = snapshot(vars);")

z = zipfile.ZipFile(SRC)
js = z.read("food-effects.js").decode("utf-8", "replace")
if ANCHOR not in js:
    print("❌ 锚点未命中")
    sys.exit(1)
njs = js.replace(ANCHOR, BRIDGE, 1)
print("已插入桥接，js len:", len(js), "->", len(njs))

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in z.infolist():
        d = z.read(info.filename)
        if info.filename == "food-effects.js":
            d = njs.encode("utf-8")
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, d)
new_zip = buf.getvalue()

old_b64 = base64.b64encode(open(SRC, "rb").read()).decode("ascii")
new_b64 = base64.b64encode(new_zip).decode("ascii")

raw = open(HTML, "rb").read().decode("utf-8", "replace")
if old_b64 not in raw:
    print("❌ index 里没找到旧 base64")
    sys.exit(1)
raw2 = raw.replace(old_b64, new_b64, 1)
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写回 index，size", len(raw2))
