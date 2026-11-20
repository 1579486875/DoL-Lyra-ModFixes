"""F36：合并重复的 setup.NPCTypeList_cn_name 赋值（幂等）。

build_all 第 1 步 inject6.py 会重建 index，可能带出两个同名字符串赋值，
后一个（63 项 / 605 字符）会覆盖前一个（225 项 / 2273 字符）。
本脚本把它们合并成一个。
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

n_pass = len(re.findall(r'<tw-passagedata[^>]*name="', data))
if n_pass < 16000:
    print(f"[F36] ❌ index 形态异常（passage={n_pass}），拒绝修改")
    sys.exit(1)

# 找所有赋值（兼容两态）
occ = []
for pat in (r'<<set setup\.NPCTypeList_cn_name to "[^"]*">>',
            r'&lt;&lt;set setup\.NPCTypeList_cn_name to "[^"]*"&gt;&gt;'):
    for m in re.finditer(pat, data):
        occ.append(m)
occ.sort(key=lambda m: m.start())

n_occ = len(occ)
if n_occ <= 1:
    print(f"[F36] 只有 {n_occ} 个赋值，无需合并")
    # 仍然校验条目数
    g = H.unescape(data)
    mm = re.search(r'setup\.NPCTypeList_cn_name\s+to\s+"([^"]*)"', g)
    if mm:
        print(f"[F36] 条目 {len(mm.group(1).split('|'))}")
    sys.exit(0)

# 解析所有表并合并
g = H.unescape(data)
tables = re.findall(r'setup\.NPCTypeList_cn_name\s+to\s+"([^"]*)"', g)
merged = {}
for t in tables:
    for x in t.split("|"):
        if "," not in x:
            continue
        k, v = x.split(",", 1)
        k, v = k.strip(), v.strip()
        if k and k not in merged:
            merged[k] = v

# 核心补充（确保关键类型存在）
EXTRA = {
    "bullboy": "牛男", "lizardgirl": "蜥蜴娘", "lizardboy": "蜥蜴男",
    "spidergirl": "蜘蛛娘", "spiderboy": "蜘蛛男",
    "harpy": "哈比", "harpygirl": "鹰身女妖", "harpyboy": "鹰身男妖",
    "none": "无", "creature": "生物", "beast": "野兽",
    "catboy": "猫男", "catgirl": "猫娘", "doggirl": "狗娘", "dogboy": "狗男",
    "wolfgirl": "狼娘", "wolfboy": "狼男", "beargirl": "熊娘", "bearboy": "熊男",
    "piggirl": "猪娘", "pigboy": "猪男", "foxgirl": "狐娘", "foxboy": "狐男",
    "cowgirl": "牛娘", "boargirl": "野猪娘", "boarboy": "野猪男",
    "dolphingirl": "海豚娘", "dolphinboy": "海豚男",
    "horsegirl": "马娘", "horseboy": "马男",
    "slimegirl": "史莱姆娘", "slimeboy": "史莱姆男",
    "plantgirl": "植物娘", "plantboy": "植物男",
    "eels": "鳗鱼", "slimes": "史莱姆", "maggots": "蛆虫",
    "slight": "瘦小", "lithe": "轻盈", "lean": "精瘦", "thin": "瘦削",
    "slender": "纤细", "lissome": "柔韧", "slim": "苗条", "taut": "紧实",
    "graceful": "优雅", "trim": "匀称", "mousy": "怯生生", "cute": "可爱",
    "fit": "健硕", "petite": "娇小", "toned": "结实", "shapely": "曲线优美",
    "robust": "强健", "plump": "丰腴", "wide-eyed": "睁大眼睛", "vulgar": "粗鄙",
    "minor demon": "小恶魔", "muscular": "肌肉发达", "curvy": "曲线玲珑",
    "plush": "柔软丰满", "voluptuous": "妖娆", "lush": "丰茂",
    "demon": "恶魔", "bulky": "魁梧", "broad": "宽阔", "lanky": "瘦长",
    "brutish": "粗野",
}
for k, v in EXTRA.items():
    if k not in merged:
        merged[k] = v

new_str = "|".join(f"{k},{v}" for k, v in merged.items()) + "|"

# 删除后面的赋值（从后往前）
for m in reversed(occ[1:]):
    start, end = m.start(), m.end()
    while start > 0 and data[start - 1] in " \t":
        start -= 1
    if start > 0 and data[start - 1] == "\n":
        start -= 1
        if start > 0 and data[start - 1] == "\r":
            start -= 1
    data = data[:start] + data[end:]

# 替换第一个（重新定位）
done = False
for pat in (r'(<<set setup\.NPCTypeList_cn_name to ")([^"]*)(">>)',
            r'(&lt;&lt;set setup\.NPCTypeList_cn_name to ")([^"]*)("&gt;&gt;)'):
    mm = re.search(pat, data)
    if mm:
        data = data[:mm.start(2)] + H.escape(new_str, quote=False) + data[mm.end(2):]
        done = True
        break

if not done:
    print("[F36] ❌ 替换失败")
    sys.exit(1)

open(HTML, "wb").write(data.encode("utf-8"))

# 校验
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
occ2 = list(re.finditer(r'setup\.NPCTypeList_cn_name\s+to\s+"([^"]*)"', g2))
n2 = len(occ2[0].group(1).split("|")) if occ2 else 0
have = {x.split(",", 1)[0].strip() for x in occ2[0].group(1).split("|") if "," in x} if occ2 else set()
CRIT = ["bullboy", "lizardgirl", "spidergirl", "harpy", "none", "creature",
        "catboy", "curvy", "eels", "guardian", "student"]
missing = [k for k in CRIT if k not in have]
ok = (len(occ2) == 1) and (n2 >= 240) and not missing
print(f"[F36] 合并 {n_occ} -> 1  条目 {n2}  缺失 {missing}  {'OK' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
