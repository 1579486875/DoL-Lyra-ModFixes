"""补 NPCTypeList_cn_name 缺的复数形式，然后重建。"""
import html as H
import os
import re

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(data)

m = re.search(r'setup\.NPCTypeList_cn_name to "([^"]{0,4000})"', g)
if not m:
    print("❌ 未找到表")
    raise SystemExit(1)

table = m.group(1)
print(f"原表长度: {len(table)}")

# 补复数形式
ADD = "eels,鳗鱼|whales,鲸鱼|lizards,蜥蜴|slimes,史莱姆|worms,蠕虫|"
need = []
for item in ADD.split("|"):
    if not item:
        continue
    k = item.split(",")[0]
    if f"{k}," not in table:
        need.append(item)

if need:
    new_table = table + "|".join(need)
    # 写回（转义形态）
    esc_old = H.escape(f'setup.NPCTypeList_cn_name to "{table}"', quote=False)
    esc_new = H.escape(f'setup.NPCTypeList_cn_name to "{new_table}"', quote=False)
    if esc_old in data:
        data = data.replace(esc_old, esc_new, 1)
        print(f"✅ 补充 {len(need)} 项: {need}")
    else:
        print("⚠️ 转义形态未匹配")
        raw_old = f'setup.NPCTypeList_cn_name to "{table}"'
        if raw_old in data:
            data = data.replace(raw_old, f'setup.NPCTypeList_cn_name to "{new_table}"', 1)
            print(f"✅ 补充 {len(need)} 项（原文形态）")
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出 ({os.path.getsize(HTML):,} 字节)")
else:
    print("（无需补充）")

# 校验
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
m2 = re.search(r'setup\.NPCTypeList_cn_name to "([^"]{0,4000})"', g2)
if m2:
    t = m2.group(1)
    for w in ["eels", "whales", "lizards", "lizard", "whale"]:
        print(f"  {w}: {'✅' if w + ',' in t else '❌'}")
