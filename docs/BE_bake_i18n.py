"""在构建期把 i18n 烤进 index.html。

效果等价于「I18nTweeReplacer 先于 TweeReplacer」：
TweeReplacer 运行时看到的就是中文文本，DoLSims / DomRobin 等
写中文锚点的补丁才能命中（实测多命中 72 条）。

注意：烤入后运行时 I18nTweeReplacer 仍会再跑一遍，但它的 f 是英文、
文本已是中文，绝大多数会失配 —— 不会重复翻译。
"""
import html
import json
import os
import re
import collections

HTML = r"E:\TAML\_dol\work\index_modded6.html"
I18N = r"E:\TAML\_dol\work\i18n_dict.json"

data = open(HTML, "rb").read().decode("utf-8", "replace")

# 按 <tw-passagedata> 切块，逐块应用
PAT = re.compile(r'(<tw-passagedata[^>]*name="([^"]+)"[^>]*>)(.*?)(</tw-passagedata>)', re.S)

d = json.load(open(I18N, "r", encoding="utf-8"))
by_p = collections.defaultdict(list)
for it in d["typeB"]["TypeBInputStoryScript"]:
    if it.get("pN"):
        by_p[it["pN"]].append(it)

total_ok = 0
total_skip = 0
changed_passages = 0

def fix_block(m):
    global total_ok, total_skip, changed_passages
    open_tag, pname, body_esc, close_tag = m.group(1), m.group(2), m.group(3), m.group(4)
    lst = by_p.get(pname)
    if not lst:
        return m.group(0)

    body = html.unescape(body_esc)
    orig = body

    for it in sorted(lst, key=lambda x: x.get("pos") or 0, reverse=True):
        f, t = it.get("f"), it.get("t")
        if not f or t is None:
            continue
        pos = it.get("pos", -1)
        if 0 <= pos <= len(body) and body[pos:pos + len(f)] == f:
            body = body[:pos] + t + body[pos + len(f):]
            total_ok += 1
        elif f in body:
            body = body.replace(f, t, 1)
            total_ok += 1
        else:
            total_skip += 1

    if body == orig:
        return m.group(0)

    changed_passages += 1
    return open_tag + html.escape(body, quote=False) + close_tag


new = PAT.sub(fix_block, data)
open(HTML, "wb").write(new.encode("utf-8"))
print(f"i18n 烤入完成")
print(f"  应用条目: {total_ok}")
print(f"  失配条目: {total_skip}")
print(f"  改动 passage: {changed_passages}")
print(f"  文件大小: {os.path.getsize(HTML):,} 字节")
