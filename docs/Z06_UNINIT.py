# -*- coding: utf-8 -*-
"""第6轮：找「$A.B 读取但 $A 从未 <<set $A to ...>> 初始化」的隐患（会抛 TypeError）。"""
import html as H
import re
from collections import defaultdict

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

# 1) 所有被 set 的顶层 SugarCube 变量
set_vars = set()
for m in re.finditer(r"<<set\s+\$([A-Za-z_]\w*)", g):
    set_vars.add(m.group(1))
for m in re.finditer(r"<(?:un)?set\s+\$([A-Za-z_]\w*)", g):
    set_vars.add(m.group(1))
print("已 <<set>> 的顶层变量:", len(set_vars))

# 2) 所有两级以上读取 $A.B
two_level = defaultdict(set)
for m in re.finditer(r"\$([A-Za-z_]\w*)\.([A-Za-z_]\w*)", g):
    two_level[m.group(1)].add(m.group(2))
print("两级访问的顶层变量:", len(two_level))

# 3) 找出从未被 set 的
never = sorted(k for k in two_level if k not in set_vars)
print("\n两级访问但从未 <<set>> 的顶层变量:", len(never))
for k in never:
    props = sorted(two_level[k])[:5]
    print("  $%-22s .%s" % (k, props))

# 4) 已知由模组/JS 注入的白名单
WHITE = {"BasicNeeds", "Phone", "timemulti", "livestock", "estate", "worn", "NPCList",
         "NPCName", "player", "crime", "daily", "outfit", "per_npc", "speech",
         "weather", "time", "settings", "options", "feats", "sexStats", "physical",
         "mental", "skills", "School", "farm", "forest", "temple", "brothel", "pub",
         "fishing", "bail", "wrenHeist", "mechanic", "market", "weekly", "stats",
         "bodywriting", "underwear", "cosmetics", "pregnancy", "npc", "kylar",
         "eden", "avery", "bailey", "robin", "whitney", "sydney", "alex", "remy",
         "greatHawk", "blackWolf", "gwylan", "wren", "doren", "leighton", "harper",
         "mason", "sam", "river", "jordan", "briar", "darren", "landry", "niki",
         "quinn", "zephyr", "ivoryWraith", "nightMonster", "corrupt", "exhib",
         "Bathroom", "toilet", "tentacle", "monster", "beast", "encounter"}
suspicious = [k for k in never if k not in WHITE]
print("\n【重点可疑】非白名单:", len(suspicious))
for k in suspicious:
    props = sorted(two_level[k])[:6]
    # 找一处上下文
    m = re.search(r"\$%s\.%s" % (re.escape(k), re.escape(props[0])), g)
    ctx = g[max(0, m.start() - 120):m.start() + 80] if m else ""
    print("  $%-20s .%-24s | %s" % (k, props[0], repr(ctx)[:160]))
