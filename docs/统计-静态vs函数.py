# -*- coding: utf-8 -*-
"""统计 170 条里：静态 name/text vs 函数式 name/text。"""
import base64
import io
import json
import re
import zipfile

raw = open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace")
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
PREFIX = "var VANILLA_TRAITS_RAW = "

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
    if (bj.get("name") or "") != "MapleBirchCE":
        continue
    t = zz.read("javascript/maplebirchce.js").decode("utf-8", "replace")
    i = t.find(PREFIX + "[")
    j = t.find("\n];", i)
    arr_text = t[i + len(PREFIX):j + 2]
    arr = json.loads(re.sub(r",\s*\]\s*$", "]", arr_text.rstrip()))
    break

print("总条数:", len(arr))

fn_name = [x for x in arr if str(x.get("name", "")).strip().startswith("(")]
fn_text = [x for x in arr if str(x.get("text", "")).strip().startswith("(")]
static = [x for x in arr if not str(x.get("name", "")).strip().startswith("(") and not str(x.get("text", "")).strip().startswith("(")]

print("函数式 name:", len(fn_name))
print("函数式 text:", len(fn_text))
print("两者都是静态（可安全翻译）:", len(static))

print("\n=== 静态条目（可翻译）===")
for k, x in enumerate(static, 1):
    print("%3d. %s | %s" % (k, x.get("name"), x.get("text")))

print("\n=== 函数式 text 的 name（name 可翻译，text 需改函数体）===")
for k, x in enumerate(fn_text, 1):
    nm = x.get("name", "")
    if str(nm).strip().startswith("("):
        continue
    print("%3d. %s" % (k, nm))
