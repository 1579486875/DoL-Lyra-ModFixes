"""D02：从 B04/C04 提取 MAP 生成 JSON。"""
import importlib.util
import json
import os
import re
import sys

WORK = r"E:\TAML\_dol\work"


def extract_map(script_path):
    """从脚本源码里提取 MAP = {...} 字典。"""
    src = open(script_path, encoding="utf-8").read()
    m = re.search(r"^MAP = \{(.*?)^\}", src, re.S | re.M)
    if not m:
        return {}
    body = m.group(1)
    # 逐行解析 "key": "value",
    out = {}
    for line in body.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        mm = re.match(r'^"((?:[^"\\]|\\.)*)"\s*:\s*"((?:[^"\\]|\\.)*)"\s*,?$', line)
        if mm:
            out[mm.group(1).replace('\\"', '"')] = mm.group(2).replace('\\"', '"')
    return out


for script, out_name in (("B04_translate_element.py", "_element_map.json"),
                         ("C04_translate_last.py", "_last_map.json")):
    p = os.path.join(WORK, script)
    if not os.path.exists(p):
        print(f"⚠️ 缺 {script}")
        continue
    d = extract_map(p)
    with open(os.path.join(WORK, out_name), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    print(f"✅ {script} -> {out_name}: {len(d)} 条")
    # 抽查
    for k in list(d)[:2]:
        print(f"    {k[:50]!r} -> {d[k][:40]!r}")
