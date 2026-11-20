"""F43（第34轮）：补全 makeFn 用的 EXTRA 表 + 让 h.orig 用最新表。"""
import html as H
import re

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(data)

# 1) 找 EXTRA 表（makeFn 用的那个）
print("=" * 90)
print("1) 找 makeFn 的 EXTRA 表")
print("=" * 90)
i = g.find("var NAMES = [\"NPC_CN_TYPE\"")
if i < 0:
    raise SystemExit("❌ 找不到包装器")

# 往前找 EXTRA = {
j = g.rfind("var EXTRA = {", 0, i)
if j < 0:
    j = g.rfind("EXTRA = {", 0, i)
print(f"  EXTRA @{j}")
seg = g[j:j + 4000]
print(f"  {seg[:600]}")

# 找 EXTRA 表的结束
k = g.find("};", j)
extra_body = g[j:k + 2]
print(f"\n  EXTRA 表长度 {len(extra_body)}")
keys = re.findall(r'"([^"]+)"\s*:', extra_body)
print(f"  {len(keys)} 键")

# 2) 需要补的
NEED = {
    # 兽人
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
    # 体格
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
add = {k: v for k, v in NEED.items() if k not in keys}
print(f"\n  要补 {len(add)} 个")

if add:
    lines = "".join('        "%s": "%s",\n' % (k, v) for k, v in add.items())
    # 在 EXTRA 表的最后一个 } 前插入
    last_brace = extra_body.rfind("}")
    new_extra = extra_body[:last_brace] + lines + "    " + extra_body[last_brace:]

    # 替换（在 data 上做，兼容两态）
    old_esc = H.escape(extra_body, quote=False)
    if old_esc in data:
        data = data.replace(old_esc, H.escape(new_extra, quote=False), 1)
    elif extra_body in data:
        data = data.replace(extra_body, new_extra, 1)
    else:
        raise SystemExit("❌ 替换失败")

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"  ✅ 已补 {len(add)} 个")

# 3) 校验
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
i2 = g2.find('var NAMES = ["NPC_CN_TYPE"')
j2 = g2.rfind("var EXTRA = {", 0, i2)
k2 = g2.find("};", j2)
keys2 = re.findall(r'"([^"]+)"\s*:', g2[j2:k2 + 2])
print(f"\n  EXTRA 现在 {len(keys2)} 键")
for kw in ("bullboy", "lizardgirl", "spidergirl", "harpy", "none", "creature", "curvy"):
    print(f"    {'✅' if kw in keys2 else '❌'} {kw}")

print(f"\n  passage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")
