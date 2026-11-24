# -*- coding: utf-8 -*-
"""直接把手机店链接静态写入 Shopping Centre passage（不依赖运行时注入）。"""
import base64
import html as H
import io
import json
import re
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")

# 1) 取出 Shopping Centre passage 的原始 HTML（未转义）
pat = re.compile(r'(<tw-passagedata[^>]*name="Shopping Centre"[^>]*>)(.*?)(</tw-passagedata>)', re.S)
m = pat.search(raw)
if not m:
    raise SystemExit("❌ 未找到 Shopping Centre passage")

head, body_esc, tail = m.group(1), m.group(2), m.group(3)
body = H.unescape(body_esc)
print("Shopping Centre 长度:", len(body))

if "手机店" in body:
    print("⚠ 已存在手机店链接，无需修改")
    raise SystemExit(0)

# 2) 找「上楼」链接，在它前面插入手机店
#    白天分支：<<stairsicon "up">><<link [[上楼 (0:02)|Shopping Centre Top]]>>
#    夜晚分支：同
MARKER = '<<stairsicon "up">><<link [[上楼 (0:02)|Shopping Centre Top]]'
cnt = body.count(MARKER)
print("找到「上楼」锚点:", cnt, "处")

if cnt == 0:
    raise SystemExit("❌ 未找到上楼锚点")

# 3) 插入内容（复用原版图标宏，白天用 Supermarket，夜晚用 Supermarket Lock 都行）
INSERT = '<<supermarketicon>><<link [[手机店 (0:01)|Shopping Centre Phone Shop]]>><<pass 1>><</link>>\n\t\t\t<br>\n\t\t\t'

# 替换所有出现（白天 + 夜晚分支都加）
new_body = body.replace(MARKER, INSERT + MARKER)
print("替换次数:", cnt)

# 4) 重新转义写回
new_esc = H.escape(new_body, quote=False)
raw2 = raw[:m.start(2)] + new_esc + raw[m.end(2):]

# 5) 校验
n1 = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
n2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", n1, "->", n2)
if n1 != n2:
    raise SystemExit("❌ passage 数变化")

if "手机店" not in H.unescape(re.search(r'<tw-passagedata[^>]*name="Shopping Centre"[^>]*>(.*?)</tw-passagedata>', raw2, re.S).group(1)):
    raise SystemExit("❌ 写入校验失败")

open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 已写入 index")

# 6) 同步把补丁模组从 index 移除（避免重复）
raw3 = raw2
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw3, re.S)
body_z = mz.group(1)
ents = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', body_z)
removed = 0
for s in ents:
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
    if "手机店" in (bj.get("name") or ""):
        # 删除这个条目
        for pat2 in ('"' + s + '",', '"' + s + '"'):
            if pat2 in body_z:
                body_z = body_z.replace(pat2, "", 1)
                removed += 1
                break
if removed:
    body_z = re.sub(r",\s*,", ",", body_z).strip().rstrip(",")
    raw4 = raw3[:mz.start(1)] + body_z + raw3[mz.end(1):]
    m4 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw4, re.S)
    print("移除补丁模组后条目:", len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', m4.group(1))))
    open(HTML, "wb").write(raw4.encode("utf-8"))
    print("✅ 已移除冗余的补丁模组")
