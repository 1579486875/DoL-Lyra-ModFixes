"""替换 settingsHeader 里的英文标题（兼容 HTML 转义形态）。

index.html 里 < > 是转义形态：&lt;div class="settingsHeader"&gt;...&lt;/div&gt;
引号是原样的。
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

TITLES = {
    "Body": "身体",
    "Head": "头部",
    "Personality": "性格",
    "Genitals": "生殖器",
    "Appearance": "外观",
    "Clothing": "衣物",
    "Skills": "技能",
    "Traits": "特质",
    "Feats": "成就",
    "Settings": "设置",
    "Statistics": "统计",
    "Cheats": "作弊",
    "Social": "社交",
    "Status": "状态",
    "Pregnancy": "怀孕",
    "Transformations": "转化",
    "Parasites": "寄生虫",
    "Fluids": "液体",
    "Reputation": "声誉",
    "Crimes": "犯罪",
    "Options": "选项",
    "General": "通用",
    "Theme": "主题",
    "Performance": "性能",
    "Info": "信息",
    "NPC Genders": "NPC性别",
    "NPC Body Parts": "NPC身体部位",
    "Pregnancy Options": "怀孕设置",
    "Body Parts": "身体部位",
    "Extra Statistics": "额外统计",
    "Mod Statistics": "模组统计",
}


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    orig = data
    total = 0

    for en, cn in TITLES.items():
        for opentag in ('&lt;div class="settingsHeader"&gt;',
                        '&lt;div class="settingsHeader options"&gt;',
                        '&lt;div class="settingsHeader bold"&gt;',
                        "<div class=\"settingsHeader\">",
                        "<div class=\"settingsHeader options\">"):
            pass
        # 用通用正则：开标签 + 任意空白 + 英文 + 任意空白 + 闭标签
        pat_esc = re.compile(
            r'(&lt;div class="settingsHeader[^"]*"&gt;)(\s*)' + re.escape(en) + r'(\s*)(&lt;/div&gt;)'
        )
        n1 = len(pat_esc.findall(data))
        if n1:
            data = pat_esc.sub(lambda m: m.group(1) + m.group(2) + cn + m.group(3) + m.group(4), data)
            total += n1
            print(f"  ✅ {en} -> {cn}: {n1} 处（转义形态）")
            continue

        pat_raw = re.compile(
            r'(<div class="settingsHeader[^"]*">)(\s*)' + re.escape(en) + r'(\s*)(</div>)'
        )
        n2 = len(pat_raw.findall(data))
        if n2:
            data = pat_raw.sub(lambda m: m.group(1) + m.group(2) + cn + m.group(3) + m.group(4), data)
            total += n2
            print(f"  ✅ {en} -> {cn}: {n2} 处（未转义）")

    print(f"\n合计 {total} 处")

    if data != orig:
        open(HTML, "wb").write(data.encode("utf-8"))
        print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")
    else:
        print("（无改动）")

    # 校验
    g = H.unescape(data)
    remain = []
    for m in re.finditer(r'<div class="settingsHeader[^"]*">(.*?)</div>', g, re.S):
        t = m.group(1).strip()
        if t and not re.search(r"[\u4e00-\u9fff]", t) and len(t) < 40:
            remain.append(t)
    print(f"\n=== 剩余纯英文标题: {len(remain)} ===")
    for t in sorted(set(remain)):
        print(f"    {t!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
