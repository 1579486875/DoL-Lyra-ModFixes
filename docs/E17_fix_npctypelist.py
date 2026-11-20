"""E17：往 setup.NPCTypeList_cn_name 里补兽人类型 + 体格词（正确修复点）。"""
import html as H
import re

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r"<tw-passagedata", data)) < 10000:
    raise SystemExit("❌ index 形态异常")

# 兽人/人类类型补充
TYPES = {
    "catboy": "猫男", "catgirl": "猫娘",
    "doggirl": "狗娘", "dogboy": "狗男",
    "wolfgirl": "狼娘", "wolfboy": "狼男",
    "beargirl": "熊娘", "bearboy": "熊男",
    "pigboy": "猪男", "piggirl": "猪娘",
    "foxgirl": "狐娘", "foxboy": "狐男",
    "dolphinboy": "海豚男", "dolphingirl": "海豚娘",
    "lizardboy": "蜥蜴男", "lizardgirl": "蜥蜴娘",
    "cowgirl": "牛娘", "bullboy": "牛男",
    "spidergirl": "蜘蛛娘", "spiderboy": "蜘蛛男",
    "harpygirl": "鹰身女妖", "harpyboy": "鹰身男妖",
    "slimegirl": "史莱姆娘", "slimeboy": "史莱姆男",
    "plantgirl": "植物娘", "plantboy": "植物男",
    "boargirl": "野猪娘", "boarboy": "野猪男",
    "horsegirl": "马娘", "horseboy": "马男",
    "beegirl": "蜂娘", "beeboy": "蜂男",
    "sheepgirl": "绵羊娘", "sheepboy": "绵羊男",
    "deergirl": "鹿娘", "deerboy": "鹿男",
    "raccoongirl": "浣熊娘", "raccoonboy": "浣熊男",
    "ratgirl": "鼠娘", "ratboy": "鼠男",
    "squidgirl": "鱿鱼娘", "squidboy": "鱿鱼男",
    "tentaclegirl": "触手娘", "tentacleboy": "触手男",
    "centaur": "半人马", "dragon": "龙",
    "creature": "生物", "horned": "长角的",
    "woman": "女人", "man": "男人", "boy": "男孩", "girl": "女孩",
    # 复数/变体（exec_verify 会测 eels）
    "eels": "鳗鱼", "dogs": "狗", "wolves": "狼", "cats": "猫", "bears": "熊",
    "horses": "马", "cows": "奶牛", "bulls": "公牛", "pigs": "猪", "foxes": "狐狸",
    "sheep": "绵羊", "deer": "鹿", "spiders": "蜘蛛", "slimes": "史莱姆",
    "plants": "植物", "snakes": "蛇", "frogs": "青蛙", "birds": "鸟",
    "tentacles": "触手", "humans": "人类", "creatures": "生物",
    "wolfgirls": "狼娘", "doggirls": "狗娘", "catgirls": "猫娘",
    "wolfboys": "狼男", "dogboys": "狗男", "catboys": "猫男",
}

# NPC 体格描述词
DESC = {
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

# 找 NPCTypeList_cn_name 赋值
# 直接在原始 data 上匹配（兼容转义形态），不 unescape 后再定位
m = None
for pat_s in (
    r'(<<set setup\.NPCTypeList_cn_name to ")([^"]*)(">>)',
    r'(&lt;&lt;set setup\.NPCTypeList_cn_name to ")([^"]*)("&gt;&gt;)',
):
    m = re.search(pat_s, data)
    if m:
        break
if not m:
    raise SystemExit("❌ 找不到 NPCTypeList_cn_name 赋值")

cur = H.unescape(m.group(2))
print(f"当前长度: {len(cur)}")

# 统计已有
have = set()
for item in cur.split("|"):
    if "," in item:
        have.add(item.split(",")[0].strip())
print(f"已有 {len(have)} 个类型")

# 组装要追加的
add_items = []
for k, v in TYPES.items():
    if k not in have:
        add_items.append(f"{k},{v}")
for k, v in DESC.items():
    if k not in have:
        add_items.append(f"{k},{v}")

print(f"要追加 {len(add_items)} 个")
for x in add_items[:8]:
    print(f"  {x}")
if len(add_items) > 8:
    print(f"  ... 还有 {len(add_items)-8} 个")

if add_items:
    new_str = cur.rstrip("|") + "|" + "|".join(add_items) + "|"
    # 替换（两态）
    old_full = m.group(0)
    new_full = m.group(1) + new_str + m.group(3) if "&lt;&lt;" in old_full else m.group(1) + new_str + m.group(3)

    # 用位置替换更安全
    start = m.start(2)
    end = m.end(2)
    data = data[:start] + new_str + data[end:]
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"\n✅ 已写入，新长度 {len(new_str)}")

# 校验
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
m2 = re.search(r'<<set setup\.NPCTypeList_cn_name to "([^"]*)"', g)
if m2:
    s = m2.group(1)
    print(f"\n=== 校验（新长度 {len(s)}）===")
    for kw in ("catboy,", "catgirl,", "doggirl,", "harpygirl,", "curvy,", "shapely,"):
        print(f"  {'✅' if kw in s else '❌'} {kw}")
    for item in s.split("|"):
        if item.startswith(("catboy,", "doggirl,", "curvy,")):
            print(f"    {item}")
print(f"  passage: {len(re.findall(r'<tw-passagedata', open(HTML,'rb').read().decode('utf-8','replace')))}")
