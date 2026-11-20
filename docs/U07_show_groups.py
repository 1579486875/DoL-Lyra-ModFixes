"""U07：只打印「确定要翻」的几组明细。"""
import json

data = json.load(open(r"E:\TAML\_dol\work\_bare_en_adverbs.json", encoding="utf-8"))

GROUPS = {
    "动作副词": ["fencing", "pressing", "slithers", "twitches", "trembles",
                 "shivers", "slithering", "twitching", "remove"],
    "兽化类型": ["wolf", "harpy", "fox", "cow", "cat", "girl", "girls"],
    "肤色": ["dark", "medium", "light"],
    "NPC名": ["Alex's Hardy Dad", "Alex's Calculating Dad", "Whitney's Uncle", "Whitney's Dad"],
    "礼仪": ["bow", "Bow"],
    "语法词": ["are", "is", "and", "their", "The", "You", "it", "my", "an"],
    "待确认": ["pussy", "man", "chest", "nectar", "women", "brittle", "meek",
               "silently", "finger", "Filters", "Help", "undies"],
}

for gname, words in GROUPS.items():
    print("\n" + "=" * 95)
    print(f"【{gname}】")
    print("=" * 95)
    for w in words:
        hs = [h for h in data if h["word"] == w]
        if not hs:
            continue
        print(f"\n  [{w}]  {len(hs)} 处")
        for h in hs[:2]:
            print(f"    {h['ctx']!r}")
