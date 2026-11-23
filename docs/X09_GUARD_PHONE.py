# -*- coding: utf-8 -*-
"""给 SmartPhone boot.json 里所有 $Phone.X 读取加 $Phone and 守卫（旧存档兼容）。"""
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
    if (bj.get("name") or "") == "SmartPhone Alpha":
        target = (s, zz, bj)
        break

if not target:
    print("❌ 未找到 SmartPhone Alpha")
    sys.exit(1)

s_old, zz, bj = target
boot = zz.read("boot.json").decode("utf-8-sig")

# 守卫规则：
# 1) <<if $Phone.X ...>>（X 前无 $Phone and 守卫）
# 2) $Phone.X 在 or/and 表达式里且整个表达式没有 $Phone and 守卫
def guard(s):
    # 已含守卫的跳过
    if "$Phone and $Phone" in s or "$Phone && $Phone" in s:
        return s
    # 把 $Phone.X 替换为 ($Phone and $Phone.X) 太复杂；改为在 <<if 后加 ($Phone and
    s2 = re.sub(r"<<if\s+(?!\$Phone\s+and\s+)(\$Phone\.)", r"<<if ($Phone and \1", s)
    s2 = re.sub(r"<<elseif\s+(?!\$Phone\s+and\s+)(\$Phone\.)", r"<<elseif ($Phone and \1", s2)
    # 括号补全：把 <<if ($Phone and $Phone.XXX ...>> 的末尾加 )
    # 简单做法：对 <<if ($Phone and ... 匹配到 >> 前加 )
    def close(m):
        inner = m.group(1)
        # 若以 ) 结尾则不动
        if inner.rstrip().endswith(")"):
            return m.group(0)
        # 计算平衡：我们只加了一层括号
        return m.group(0)[:0] + "<<if (" + inner + ")" + m.group(0)[len("<<if (" + inner):]
    s2 = re.sub(r"<<(if|elseif)\s+\(\$Phone and ([^<>]*?)>>", lambda mm: "<<%s ($Phone and %s)>>" % (mm.group(1), mm.group(2)), s2)
    return s2

boot2 = guard(boot)

# 统计变化
cnt = boot2.count("($Phone and") - boot.count("($Phone and")
print("新增守卫:", cnt)

# 验证 JSON
json.loads(boot2)
print("JSON 合法")

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zz.infolist():
        d = zz.read(info.filename)
        if info.filename == "boot.json":
            d = boot2.encode("utf-8")
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
