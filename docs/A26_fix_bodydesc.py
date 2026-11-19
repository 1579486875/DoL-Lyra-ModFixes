"""A26：修 NPC description 里的英文体格词（Curvy 等）。"""
import html as H
import os
import re

WORK = r"E:\TAML\_dol\work"
HTML = os.path.join(WORK, "index_modded6.html")
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r"<tw-passagedata", data)) < 10000:
    print("❌ index 不是明文形态")
    raise SystemExit(1)

print("=" * 90)
print("1) 找 description 的显示处")
print("=" * 90)
n = 0
for m in re.finditer(r"(?:\.|\$)description\b", data):
    ctx = data[max(0, m.start() - 180):m.start() + 180]
    if any(k in ctx for k in ("<<=", "${", "<<print", "capitalise", "toUpperFirst", "ucfirst")):
        n += 1
        print(f"\n  @{m.start()}: {ctx!r}")
        if n >= 6:
            break
print(f"  共 {n} 处带显示特征")

print("\n" + "=" * 90)
print("2) 查 NPC_CN_TYPE 的 EXTRA 表是否含体格词")
print("=" * 90)
m = re.search(r"var EXTRA = \{(.*?)\};", data, re.S)
if m:
    body = m.group(1)
    have = set(re.findall(r'"([a-z \-]+)"\s*:', body))
    WORDS = ["slight", "lithe", "lean", "thin", "slender", "lissome", "slim",
             "taut", "graceful", "trim", "mousy", "cute", "fit", "petite",
             "toned", "shapely", "robust", "plump", "wide-eyed", "vulgar",
             "minor demon", "muscular", "curvy", "plush", "voluptuous",
             "lush", "demon", "bulky", "broad", "lanky", "brutish",
             "tutorial", "debug"]
    missing = [w for w in WORDS if w not in have]
    print(f"  EXTRA 有 {len(have)} 键，体格词缺 {len(missing)} 个")
    print(f"  缺: {missing}")

print("\n" + "=" * 90)
print("3) 给 EXTRA 补体格词")
print("=" * 90)
ADD = {
    "slight": "瘦小", "lithe": "轻盈", "lean": "精瘦", "thin": "瘦削",
    "slender": "纤细", "lissome": "柔韧", "slim": "苗条", "taut": "紧实",
    "graceful": "优雅", "trim": "匀称", "mousy": "怯生生", "cute": "可爱",
    "fit": "健硕", "petite": "娇小", "toned": "结实", "shapely": "曲线优美",
    "robust": "强健", "plump": "丰腴", "wide-eyed": "睁大眼睛", "vulgar": "粗鄙",
    "minor demon": "小恶魔", "muscular": "肌肉发达", "curvy": "曲线玲珑",
    "plush": "柔软丰满", "voluptuous": "妖娆", "lush": "丰茂",
    "demon": "恶魔", "bulky": "魁梧", "broad": "宽阔", "lanky": "瘦长",
    "brutish": "粗野", "tutorial": "教程", "debug": "调试",
}

if m:
    body = m.group(1)
    have = set(re.findall(r'"([a-z \-]+)"\s*:', body))
    add = []
    for k, v in ADD.items():
        if k not in have:
            add.append('            "%s": "%s",' % (k, v))
    if add:
        nb = body.rstrip()
        if not nb.endswith(","):
            nb += ","
        nb += "\n" + "\n".join(add) + "\n        "
        data = data[:m.start(1)] + nb + data[m.end(1):]
        open(HTML, "wb").write(data.encode("utf-8"))
        print(f"  ✅ 补了 {len(add)} 个")
    else:
        print("  （已全有）")

# 校验
g = open(HTML, "rb").read().decode("utf-8", "replace")
print("\n" + "=" * 90)
print("4) 校验")
print("=" * 90)
print(f"  passage: {len(re.findall(r'<tw-passagedata', g))}")
m2 = re.search(r"var EXTRA = \{(.*?)\};", g, re.S)
if m2:
    have2 = set(re.findall(r'"([a-z \-]+)"\s*:', m2.group(1)))
    print(f"  EXTRA 键数: {len(have2)}")
    for kw in ["curvy", "slight", "shapely", "voluptuous", "muscular"]:
        print(f"    {'✅' if kw in have2 else '❌'} {kw}")
