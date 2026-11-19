"""最终修复 NPCTypeList_cn_name：清粘连 + 补复数。放在 build_all 末尾。"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

PLURALS = ["eels,鳗鱼", "whales,鲸鱼", "lizards,蜥蜴", "slimes,史莱姆",
           "worms,蠕虫", "spiders,蜘蛛", "maggots,蛆虫", "wasps,黄蜂",
           "bees,蜜蜂", "squids,鱿鱼", "vines,藤蔓", "slugs,蛞蝓",
           "tentacles,触手", "lurkers,潜伏者", "snakes,蛇", "fish,鱼"]


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    g = H.unescape(data)

    m = re.search(r'(setup\.NPCTypeList_cn_name to ")([^"]+)(")', g)
    if not m:
        print("❌ 未找到表")
        return 1

    table = m.group(2)
    orig_len = len(table)

    # 1) 清粘连：把 `xxx中文eels,` 这种拆开
    for p in PLURALS:
        key = p.split(",")[0]
        # 形如 <非|>key,  且 key 前面不是 |
        table = re.sub(r"([^|])(" + re.escape(key) + r"),", r"\1|\2,", table)

    # 2) 补缺失的复数
    added = []
    for p in PLURALS:
        key = p.split(",")[0]
        if f"{key}," not in table:
            table = table.rstrip("|") + "|" + p
            added.append(p)

    if table == m.group(2):
        print("  ✅ 表无需修改")
        return 0

    print(f"  清理 + 补充 {len(added)} 项: {added}")

    # 写回（转义形态）
    esc_old = H.escape(m.group(1) + m.group(2) + m.group(3), quote=False)
    esc_new = H.escape(m.group(1) + table + m.group(3), quote=False)
    if esc_old in data:
        data = data.replace(esc_old, esc_new, 1)
    else:
        data = data.replace(m.group(1) + m.group(2) + m.group(3),
                            m.group(1) + table + m.group(3), 1)
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"  表长度 {orig_len} -> {len(table)}")

    # 校验
    g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
    m2 = re.search(r'setup\.NPCTypeList_cn_name to "([^"]+)"', g2)
    t = m2.group(1)
    print("\n=== 校验 ===")
    for w in ["eels", "whale", "lizard", "slime", "worm", "spider", "maggot",
              "wasp", "bee", "squid", "vine", "slug", "tentacle", "lurker",
              "fish", "snake"]:
        print(f"  {w + ',':<14} {'✅' if w + ',' in t else '❌'}")
    # 检查粘连
    bad = re.findall(r"[^\|](eels|whales|lizards|slimes|worms),", t)
    print(f"\n  粘连残留: {len(bad)}  {bad[:5]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
