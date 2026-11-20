"""AB05：查几类边界模糊的英文短语的上下文，判断玩家是否可见。"""
import html as H
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

TARGETS = [
    ("Outside temperature:", "温度面板"),
    ("Body temperature:", "温度面板"),
    ("It's cold outside.", "天气描述"),
    ("Not enough money", "商店提示"),
    ("New clothes are available at the forest shop:", "通知"),
    ("Colours to choose from:", "染色 UI"),
    ("Copied to clipboard!", "复制提示"),
    ("Invalid code.", "输入错误"),
    ("DEBUG OPTIONS", "调试面板"),
    ("Hypnotic Devotion", "催眠状态"),
    ("Halloween clothes", "服装分类"),
    ("Consider asking Avery to attend.", "提示"),
]

for pat, label in TARGETS:
    print("=" * 95)
    print(f"[{label}]  {pat!r}")
    print("=" * 95)
    ms = list(re.finditer(r"<span(?:\s[^>]*)?>([^<]{0,80}" + re.escape(pat.split(":")[0]) + r"[^<]{0,80})</span>", g))
    if not ms:
        ms = list(re.finditer(re.escape(pat), g))
    for m in ms[:1]:
        print(f"  {g[max(0, m.start() - 350):m.start() + 350]!r}")
    print()
