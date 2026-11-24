# -*- coding: utf-8 -*-
"""第5轮：验证特质表完整性 + 中文覆盖 + 结构未被破坏。"""
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

    print("=== 结构完整性 ===")
    print("  表起始:", i, " 表结束:", j)
    if i < 0 or j < 0:
        print("❌ 表定位失败")
        break

    arr_text = t[i + len(PREFIX):j + 2]
    arr_clean = re.sub(r",\s*\]\s*$", "]", arr_text.rstrip())
    try:
        arr = json.loads(arr_clean)
        print("  ✅ JSON 解析成功，条目:", len(arr))
    except Exception as e:
        print("  ❌ JSON 解析失败:", e)
        break

    # 必需字段
    bad = [x for x in arr if not all(k in x for k in ("cat", "name", "has", "text"))]
    print("  缺字段条目:", len(bad))

    # 中文覆盖
    cn_name = sum(1 for x in arr if re.search(r"[\u4e00-\u9fff]", str(x.get("name", ""))))
    cn_text = sum(1 for x in arr if re.search(r"[\u4e00-\u9fff]", str(x.get("text", ""))))
    fn_text = sum(1 for x in arr if str(x.get("text", "")).strip().startswith("("))
    fn_name = sum(1 for x in arr if str(x.get("name", "")).strip().startswith("("))
    print("\n=== 中文覆盖 ===")
    print("  name 中文: %d / %d = %.1f%%" % (cn_name, len(arr), cn_name * 100.0 / len(arr)))
    print("  text 中文: %d / %d = %.1f%%" % (cn_text, len(arr), cn_text * 100.0 / len(arr)))
    print("  函数式 name: %d（无法翻译）" % fn_name)
    print("  函数式 text: %d（无法翻译）" % fn_text)
    print("  静态 text 中文率: %.1f%%" % (cn_text * 100.0 / (len(arr) - fn_text) if len(arr) > fn_text else 0))

    # 分类
    from collections import Counter
    print("\n=== 分类分布 ===")
    for k, v in Counter(x.get("cat", "?") for x in arr).most_common():
        print("  %-20s %d" % (k, v))

    # 抽 8 条看内容
    print("\n=== 抽样 8 条 ===")
    for x in arr[:3] + arr[70:72] + arr[140:143]:
        print("  [%s] %s" % (x.get("cat"), x.get("name")))
        print("     %s" % str(x.get("text"))[:60])
    break
