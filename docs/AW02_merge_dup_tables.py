"""AW02（第13轮）：合并被重复赋值的 setup.*_cn_name 字符串翻译表（幂等，模板 §5.20 同类）。

现象：Widgets variablesStatic 里 NPCNameList_cn_name / NPCTitleList_cn_name 各被赋值两次——
  第一次是官方汉化（i18n.json 原文），第二次是早期构建脚本 AD_direct_patch 注入的临时表。
  后者覆盖前者，于是：
    · 角色名与正文不一致：Jordan 正文「约旦」(520 处) 而名字处显示「乔丹」；River 瑞沃/里弗、Wren 伦恩/雷恩、
      Alex 艾利克斯/亚历克斯、Sirris 西里斯/茜里斯、Niki 尼奇/妮基、Sam 萨姆/山姆、Charlie 查里/查理、Kylar 凯拉尔/凯拉 …
    · 头衔表从 1072 字符缩成 605 字符，businessperson / crimson hound 等官方已译的头衔变回英文。
修法（①保意图）：以官方表为准，临时表里官方没有的键（模组 NPC 等）追加在后面；只保留第一处赋值。
"""
import html as H
import json
import os
import re
import sys

sys.path.insert(0, r"E:\TAML\_dol\work")
import modzip_lib as MZ

HTML = os.environ.get("DOL_HTML") or r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")
if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[AW02] index 形态异常")
    sys.exit(1)

d = json.loads(MZ.read_mod_file(data, "ModI18N", "i18n.json").decode("utf-8-sig"))
official = {}
for v in d["typeB"]["TypeBInputStoryScript"]:
    for m in re.finditer(r'<<set setup\.(\w+_cn_name) to "([^"]*)"', v["t"]):
        official.setdefault(m.group(1), m.group(2))

PAT = re.compile(r'&lt;&lt;set setup\.(\w+_cn_name) to "([^"]*)"&gt;&gt;')
occ = {}
for m in PAT.finditer(data):
    occ.setdefault(m.group(1), []).append(m)


def parse(s):
    out = []
    for p in s.split("|"):
        if "," in p:
            k, v = p.split(",", 1)
            if k.strip() and v.strip():
                out.append((k.strip(), v.strip()))
    return out


edits = []
report = []
for key, ms in occ.items():
    if len(ms) < 2:
        continue
    vals = [H.unescape(m.group(2)) for m in ms]
    off = official.get(key)
    base = off if off in vals else vals[0]
    merged, seen = [], set()
    for k, v in parse(base):
        if k.lower() not in seen:
            merged.append((k, v))
            seen.add(k.lower())
    added = []
    for val in vals:
        for k, v in parse(val):
            if k.lower() not in seen:
                merged.append((k, v))
                seen.add(k.lower())
                added.append(k)
    new_val = "|".join(k + "," + v for k, v in merged)
    first = ms[0]
    edits.append((first.start(), first.end(), H.escape('<<set setup.%s to "%s">>' % (key, new_val), quote=False)))
    for m in ms[1:]:
        edits.append((m.start(), m.end(), ""))
    report.append("%s：%d 次赋值 → 1（以%s为准，追加 %d 键 %s）" % (
        key, len(ms), "官方表" if off in vals else "第一处", len(added), added[:8]))

if not edits:
    print("[AW02] 无重复赋值的翻译表，跳过")
    sys.exit(0)
for s, e, rep in sorted(edits, reverse=True):
    data = data[:s] + rep + data[e:]
open(HTML, "wb").write(data.encode("utf-8"))
for r in report:
    print("[AW02]", r)
print("[AW02] OK")
