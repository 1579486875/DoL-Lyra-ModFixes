"""直接替换 widget 里硬编码的英文状态名（不依赖 i18n）。

这些名字在 <<widget "paincaption">> 等里面是裸文本：
    <div @class="...">
        Pain:
        <<if $options.showCaptionText is true>>

i18n 里有对应条目但 pos 偏移导致没应用，直接改。
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

# (英文, 中文)
NAMES = [
    ("Pain:", "疼痛："),
    ("Arousal:", "性奋："),
    ("Fatigue:", "疲劳："),
    ("Stress:", "压力："),
    ("Trauma:", "创伤："),
    ("Control:", "自控："),
    ("Allure:", "诱惑："),
    ("Purity:", "纯洁："),
    ("Corruption:", "堕落："),
    ("Lust:", "性欲："),
    ("Sensitivity:", "敏感度："),
    ("Wetness:", "湿润度："),
    ("Tiredness:", "疲惫度："),
    ("Temperature:", "体温："),
    ("Alcohol:", "酒精："),
    ("Drugs:", "药物："),
    ("Hallucinogens:", "致幻："),
    ("Hunger:", "饥饿："),
    ("Thirst:", "口渴："),
    ("Bladder:", "小便："),
    ("Bowels:", "大便："),
    ("Filth:", "脏污度："),
    ("Mood:", "心情："),
    ("Teeth:", "牙齿："),
    ("Hair:", "头发："),
    ("Fear:", "恐惧："),
    ("Awareness:", "意识："),
    ("Promiscuity:", "淫乱："),
    ("Exhibitionism:", "暴露癖："),
    ("Deviancy:", "异种癖："),
    ("Sadism:", "施虐癖："),
    ("Masochism:", "受虐癖："),
    ("Bestiality:", "兽交癖："),
]

# 场景 A：widget 里的裸文本形态（行首缩进 + 名字 + 换行）
#   形如 "\n\t\t\t\tPain:\n"
PAT_LINE = re.compile(r"(\n[ \t]+)([A-Z][A-Za-z]+):(\s*\n)")


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    orig = data

    mapped = dict(NAMES)
    hits = 0

    def repl(m):
        nonlocal hits
        name = m.group(2) + ":"
        if name in mapped:
            hits += 1
            return m.group(1) + mapped[name] + m.group(3)
        return m.group(0)

    data = PAT_LINE.sub(repl, data)
    print(f"场景 A（行首裸文本）: {hits} 处")

    # 场景 B：JS displayName: "Xxx:"  -> displayName: "中文："
    hits2 = 0

    def repl2(m):
        nonlocal hits2
        key = m.group(2) + ":"
        if key in mapped:
            hits2 += 1
            return m.group(1) + '"' + mapped[key] + '"'
        return m.group(0)

    data = re.sub(r'(displayName:\s*)"([A-Z][A-Za-z]+):"', repl2, data)
    print(f"场景 B（displayName）: {hits2} 处")

    # 场景 C：textMap 里的英文选项
    TMAP = {
        "Penis": "阴茎", "Vagina": "阴道", "Hermaphrodite": "两者",
        "Male": "男性", "Female": "女性", "Neither": "中性",
    }
    hits3 = 0
    for en, cn in TMAP.items():
        pat = re.compile(r'(textMap:\s*\{[^}]*?"[a-z]":\s*")' + re.escape(en) + r'(")')
        n = len(pat.findall(data))
        if n:
            data = pat.sub(r"\1" + cn + r"\2", data)
            hits3 += n
    print(f"场景 C（textMap）: {hits3} 处")

    print(f"\n合计 {hits + hits2 + hits3} 处")

    if data != orig:
        open(HTML, "wb").write(data.encode("utf-8"))
        print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")
    else:
        print("⚠️ 无改动")

    # 校验
    g = H.unescape(data)
    print("\n=== 校验（应全为 0）===")
    for en, cn in NAMES[:12]:
        n = len(re.findall(r"\n[ \t]+" + re.escape(en) + r"\s*\n", g))
        if n:
            print(f"  ❌ {en}: {n} 处")
    print("  （未列出的即已清零）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
