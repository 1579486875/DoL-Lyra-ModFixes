"""修复 <<cheats-npcs>>：i18n 用了不存在的 $NPCNameList。

关键教训：$NPCNameList 是合法存档变量（V.NPCNameList 的别名），全库 97 处，
         绝不能全局替换。只改 cheats-npcs widget 内部的两处。

实际内容（i18n 加的）：
  <<set _NPCNameList_cn to {}>><<run $NPCNameList.forEach((x)=>_NPCNameList_cn[setup.NPC_CN_NAME(x)] = x)>>
  ...<<optionsfrom _NPCNameList_cn>>...
  ...<<initNNPCVirginity $NPCNameList.indexOf(_npcId)>>...

但 i18n 自己在 `<<set _NPCNameList_cn to {}>>` 里就用了未定义的 $NPCNameList，
导致 forEach 抛错 → _NPCNameList_cn 仍是 {} → <<optionsfrom {}>> 报
"expression must yield a supported collection or generic object"

修复（仅限 widget 内部，共 2 处）：
  $NPCNameList.forEach  → (setup.NPCNameList || $NPCNameList || []).forEach
  $NPCNameList.indexOf  → (setup.NPCNameList || $NPCNameList || []).indexOf
"""
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

WIDGET_START_CANDIDATES = ['&lt;&lt;widget "cheats-npcs"&gt;&gt;', '<<widget "cheats-npcs">>']
WIDGET_END = "<</widget>>"


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")

    i = -1
    used = None
    for cand in WIDGET_START_CANDIDATES:
        i = data.find(cand)
        if i >= 0:
            used = cand
            break
    if i < 0:
        print("❌ 找不到 cheats-npcs widget")
        return 1
    print(f"   使用形态: {used!r}")
    WIDGET_END_LOCAL = "&lt;&lt;/widget&gt;&gt;" if used.startswith("&lt;") else "<</widget>>"
    j = data.find(WIDGET_END_LOCAL, i)
    if j < 0:
        print("❌ 找不到 widget 结束")
        return 1
    j += len(WIDGET_END_LOCAL)

    body = data[i:j]
    orig = body

    # 只在这个 widget 内替换，且用安全的回落写法
    body = body.replace(
        "$NPCNameList.forEach",
        "(setup.NPCNameList || $NPCNameList || []).forEach",
    )
    body = body.replace(
        "$NPCNameList.indexOf",
        "(setup.NPCNameList || $NPCNameList || []).indexOf",
    )

    if body == orig:
        print("⚠️  widget 内没有需要改的引用（可能已修过）")
        return 0

    data = data[:i] + body + data[j:]
    open(HTML, "wb").write(data.encode("utf-8"))

    n1 = orig.count("$NPCNameList.forEach")
    n2 = orig.count("$NPCNameList.indexOf")
    print(f"✅ cheats-npcs 内修正: forEach {n1} 处 / indexOf {n2} 处")

    # 校验：全局 setup.NPCNameList 不应因此增加过多
    total = data.count("setup.NPCNameList")
    print(f"   全局 setup.NPCNameList 出现 {total} 处（只应是 widget 内的 2 处）")

    # 打印修改后的关键行
    g = data[i:data.find(WIDGET_END_LOCAL, i)]
    for kw in ("_NPCNameList_cn to", "initNNPCVirginity"):
        k = g.find(kw)
        if k >= 0:
            print(f"   [{kw}] {g[max(0,k-60):k+180]!r}")

    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
