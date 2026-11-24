# -*- coding: utf-8 -*-
"""应用翻译到 VANILLA_TRAITS_RAW（先 dry-run）。"""
import base64
import importlib.util
import io
import json
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
PREFIX = "var VANILLA_TRAITS_RAW = "
DRY = "--write" not in sys.argv


def load_table(fname, attr):
    spec = importlib.util.spec_from_file_location(fname, r"E:\TAML\_dol\work\%s.py" % fname)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return getattr(m, attr)


TRANS = {}
TRANS.update(load_table("翻译表-1", "TRANS_1"))
TRANS.update(load_table("翻译表-2", "TRANS_2"))
FN_NAME = load_table("翻译表-2", "TRANS_FN_NAME")
print("静态翻译表:", len(TRANS), "条")
print("函数式 name 翻译:", len(FN_NAME), "条")

raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)

target = None
for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1)):
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
    if (bj.get("name") or "") == "MapleBirchCE":
        target = (s, zz, bj)
        break

if not target:
    print("❌ 未找到")
    sys.exit(1)

s_old, zz, bj = target
t = zz.read("javascript/maplebirchce.js").decode("utf-8", "replace")

i = t.find(PREFIX + "[")
j = t.find("\n];", i)
arr_text = t[i + len(PREFIX):j + 2]
arr = json.loads(re.sub(r",\s*\]\s*$", "]", arr_text.rstrip()))
print("解析条目:", len(arr))

cnt_static = 0
cnt_fn = 0
miss = []
for item in arr:
    nm = item.get("name", "")
    nm_s = str(nm)
    # 函数式 name 跳过
    if nm_s.strip().startswith("("):
        continue
    if nm in TRANS:
        cn_name, cn_text = TRANS[nm]
        tx = item.get("text", "")
        # 只翻静态 text
        if not str(tx).strip().startswith("("):
            item["name"] = cn_name
            item["text"] = cn_text
            cnt_static += 1
        else:
            # 函数式 text：只翻 name
            item["name"] = cn_name
            cnt_fn += 1
    elif nm in FN_NAME:
        item["name"] = FN_NAME[nm]
        cnt_fn += 1
    else:
        if not re.search(r"[\u4e00-\u9fff]", nm_s):
            miss.append(nm_s)

print("翻译（静态 name+text）:", cnt_static)
print("翻译（仅 name）:", cnt_fn)
print("仍未覆盖:", len(miss))
for x in miss[:20]:
    print("   ", x[:70])

if DRY:
    print("\n[dry-run] 未写入。加 --write 执行。")
    sys.exit(0)

# 序列化
lines = [json.dumps(x, ensure_ascii=False, separators=(",", ":")) for x in arr]
new_arr = "[\n    " + ",\n  ".join(lines) + "\n]"

# 校验
try:
    chk = json.loads(new_arr)
    assert len(chk) == len(arr), "条目数变化"
    print("回读校验: %d 条 ✓" % len(chk))
except Exception as e:
    print("❌ 校验失败:", e)
    sys.exit(1)

t2 = t[:i + len(PREFIX)] + new_arr + t[j + 2:]

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zz.infolist():
        d = zz.read(info.filename)
        if info.filename == "javascript/maplebirchce.js":
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
