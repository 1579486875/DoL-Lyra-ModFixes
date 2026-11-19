"""修用户截图里的未翻译项。

1) Genitals: -> 生殖器：
2) Makeup（仪态第一项）-> 妆容
3) a light -> 浅色
4) You have -> 你有
5) 寄生虫名 Eel/Slime/Worm/Maggot/Spider -> 中文
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

# ---- 1) faceVariantOptions 补「妆容」键（现在 _faceVariantscn 是 Object.keys，安全）----
FV_OLD = '''<<set setup.faceVariantOptions to {
		"default": {
			"温柔": "default",
			"妩媚": "catty",
			"高冷": "aloof",
			"甜美": "sweet",
			"勾人": "foxy",
			"忧郁": "gloomy",
		},
	}>>'''
FV_NEW = '''<<set setup.faceVariantOptions to {
		"default": {
			"温柔": "default",
			"妩媚": "catty",
			"高冷": "aloof",
			"甜美": "sweet",
			"勾人": "foxy",
			"忧郁": "gloomy",
			"妆容": "makeup",
		},
	}>>'''

# ---- 2) 直接文本替换 ----
PAIRS = [
    # Genitals: 标题
    (">Genitals:<", ">生殖器：<"),
    (">\n\t\t\t\tGenitals:\n\t\t\t<", ">\n\t\t\t\t生殖器：\n\t\t\t<"),
    # displayName
    ('displayName: "Genitals:"', 'displayName: "生殖器："'),
    # 外观描述片段
    ("你有着 a light 的皮肤", "你有着 浅色 的皮肤"),
    ("You have 一个阴道", "你有一个阴道"),
    ("You have 一个阴茎", "你有一个阴茎"),
]

# ---- 3) 寄生虫名（_parasiteTypes 数组里的英文项）----
PARASITE = {
    '"eels"': '"鳗鱼"',
    '"slimes"': '"史莱姆"',
    '"worms"': '"蠕虫"',
    '"maggots"': '"蛆虫"',
    '"spiders"': '"蜘蛛"',
    '"fish"': '"鱼"',
    '"snake"': '"蛇"',
    '"tentacle"': '"触手"',
    '"lurker"': '"潜伏者"',
    '"wasp"': '"黄蜂"',
    '"bee"': '"蜜蜂"',
    '"squid"': '"乌贼"',
    '"vine"': '"藤蔓"',
    '"slug"': '"蛞蝓"',
}


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    total = 0

    # faceVariantOptions
    for a, b in ((H.escape(FV_OLD, quote=False), H.escape(FV_NEW, quote=False)), (FV_OLD, FV_NEW)):
        if a in data:
            data = data.replace(a, b, 1)
            total += 1
            print("  ✅ faceVariantOptions 补「妆容」键")
            break

    # 普通替换
    for old, new in PAIRS:
        for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
            if a in data:
                n = data.count(a)
                data = data.replace(a, b)
                total += n
                print(f"  ✅ {old[:40]!r} -> {new[:40]!r}  ({n} 处)")
                break

    # 寄生虫名：只在 _parasiteTypes 数组里替换
    m = re.search(r'<<set _parasiteTypes to \[([^\]]*)\]>>', data)
    if m:
        arr = m.group(1)
        new_arr = arr
        for en, cn in PARASITE.items():
            new_arr = new_arr.replace(en, cn)
        if new_arr != arr:
            data = data[:m.start(1)] + new_arr + data[m.end(1):]
            total += 1
            print(f"  ✅ _parasiteTypes 数组已中文化")

    print(f"\n合计 {total} 处")

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")

    # 校验
    g = H.unescape(data)
    print("\n=== 校验 ===")
    print(f"  faceVariantOptions 含妆容: {'\"妆容\": \"makeup\"' in g}")
    m2 = re.search(r'<<set _parasiteTypes to \[([^\]]*)\]>>', g)
    if m2:
        print(f"  寄生虫数组: {m2.group(1)[:200]}")
    print(f"  'a light' 残留: {g.count('a light')}")
    print(f"  'You have' 残留: {g.count('You have')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
