# -*- coding: utf-8 -*-
"""把 NPC.Avatars 的 bsa-check.twee 英文分支改成中文（统一走中文，删除 ModI18N 判断）。"""
import base64
import io
import json
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1))

target = None
for s in parts:
    try:
        d = base64.b64decode(re.sub(r"\s+", "", s))
    except Exception:
        continue
    if d[:2] != b"PK":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(d))
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
    except Exception:
        continue
    if "NPC Avatars" in (bj.get("name") or ""):
        target = (s, zz, bj)
        break

if not target:
    print("❌ 未找到 NPC.Avatars")
    sys.exit(1)

s_old, zz, bj = target
print("命中:", bj.get("name"), bj.get("version"))
t = zz.read("game/base-system/ovelays/bsa-check.twee").decode("utf-8", "replace")

# 替换 1：无图像提示
OLD1 = '''        <<if window.modUtils.getMod('ModI18N')>>

            <mouse class="tooltip-small linkBlue">

                <span class="red">为什么没有图像？</span>

                <span>您尚未启用模组图像，请打开Mod管理器，在“BeautySelectorAddon 启用及排序管理”选中此Mod，然后点击“启用选中的Type”，重新载入后即可看到图像。</span>

            </mouse>

        <<else>>

            <mouse class="tooltip-small linkBlue">

                <span class="red">Why are there no images?</span>

                <span>You haven’t enabled mod images yet. Please open the ModLoader Manager, select this mod under “BeautySelectorAddon Type Enable And Order Manager”, then click “Enable Selected Type”. Reload the game and the images will appear.</span>

            </mouse>

        <</if>>'''
NEW1 = '''        <mouse class="tooltip-small linkBlue">

            <span class="red">为什么没有图像？</span>

            <span>您尚未启用模组图像，请打开Mod管理器，在“BeautySelectorAddon 启用及排序管理”选中此Mod，然后点击“启用选中的Type”，重新载入后即可看到图像。</span>

        </mouse>'''

# 替换 2：说明
OLD2 = '''        <<if window.modUtils.getMod('ModI18N')>>

            <mouse class="tooltip-small linkBlue">

                图像说明

                <span>您已使用NPC头像增添模组。游戏并未提供各位角色的具体形象，头像为模组二次创作，仅供爱好者交流，请勿将其当作官方形象。</span>

            </mouse>

        <<else>>

            <mouse class="tooltip-small linkBlue">

                Image Instructions

                <span>You are using the NPC Avatars Mod. The character portraits are fan-made, as the game does not provide official appearances for these characters. Please do not consider them to be official representations.</span>

            </mouse>

        <</if>>'''
NEW2 = '''        <mouse class="tooltip-small linkBlue">

            图像说明

            <span>您已使用NPC头像增添模组。游戏并未提供各位角色的具体形象，头像为模组二次创作，仅供爱好者交流，请勿将其当作官方形象。</span>

        </mouse>'''

n1 = t.count(OLD1)
n2 = t.count(OLD2)
print("匹配：无图像提示 %d 处，说明 %d 处" % (n1, n2))

if n1 == 0 and n2 == 0:
    print("❌ 未匹配，检查空白字符")
    sys.exit(1)

t2 = t.replace(OLD1, NEW1).replace(OLD2, NEW2)
print("改后长度:", len(t), "->", len(t2))

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zz.infolist():
        d = zz.read(info.filename)
        if info.filename == "game/base-system/ovelays/bsa-check.twee":
            d = t2.encode("utf-8")
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, d)

new_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
raw2 = raw.replace(s_old, new_b64, 1)

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
if npass2 != npass:
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
