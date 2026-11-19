"""修复 faceVariantOptions 引发的 undefined 连锁。

问题：
  上一轮给 setup.faceVariantOptions["default"] 加了 妆容/裸妆/模组1-15 共 17 个键，
  但 cheatsDemeanour 里 _faceVariantscn 是硬编码的 6 项数组，
  循环按 Object.values(...).length（23）跑 → 后 17 项显示 undefined。
  截图里「举止：温柔|妩媚|高冷|甜美|勾人|忧郁|undefined|undefined|...」就是它。

修复：
  1) 撤销那 17 个键（恢复原 6 项，与 i18n 的 _faceVariantscn 对齐）
  2) 把 _faceVariantscn 改成 Object.keys(setup.faceVariantOptions[V.facestyle])
     —— 键名本来就是中文，数量永远与 values 对齐，以后再加也不会错
"""
import html as H
import os
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

# 当前（被改坏的）23 键版本
CUR = '''<<set setup.faceVariantOptions to {
		"default": {
			"温柔": "default",
			"妩媚": "catty",
			"高冷": "aloof",
			"甜美": "sweet",
			"勾人": "foxy",
			"忧郁": "gloomy",
			"妆容": "makeup",
			"裸妆": "red",
			"模组1": "modded1",
			"模组2": "modded2",
			"模组3": "modded3",
			"模组4": "modded4",
			"模组5": "modded5",
			"模组6": "modded6",
			"模组7": "modded7",
			"模组8": "modded8",
			"模组9": "modded9",
			"模组10": "modded10",
			"模组11": "modded11",
			"模组12": "modded12",
			"模组13": "modded13",
			"模组14": "modded14",
			"模组15": "modded15",
		},
	}>>'''

ORIG = '''<<set setup.faceVariantOptions to {
		"default": {
			"温柔": "default",
			"妩媚": "catty",
			"高冷": "aloof",
			"甜美": "sweet",
			"勾人": "foxy",
			"忧郁": "gloomy",
		},
	}>>'''

# 硬编码的 6 项中文名 → 动态取键
OLD_CN = '<<set _faceVariantscn = ["温柔", "妩媚", "高冷", "甜美", "勾人", "忧郁"]>>'
NEW_CN = '<<set _faceVariantscn = Object.keys(setup.faceVariantOptions[V.facestyle])>>'

# 同样处理 _faceStylescn（如果也是硬编码）
OLD_STYLE = None


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    ok = 0

    # 1) 撤销 17 个键
    for old, new, label in [
        (CUR, ORIG, "撤销 faceVariantOptions 的 17 个键"),
    ]:
        e_old, e_new = H.escape(old, quote=False), H.escape(new, quote=False)
        if e_old in data:
            data = data.replace(e_old, e_new, 1)
            ok += 1
            print(f"  ✅ {label}")
        elif old in data:
            data = data.replace(old, new, 1)
            ok += 1
            print(f"  ✅ {label}（未转义）")
        else:
            print(f"  ❌ {label} —— 未匹配")

    # 2) _faceVariantscn 动态化
    e_old, e_new = H.escape(OLD_CN, quote=False), H.escape(NEW_CN, quote=False)
    if e_old in data:
        data = data.replace(e_old, e_new, 1)
        ok += 1
        print("  ✅ _faceVariantscn 改为动态取键")
    elif OLD_CN in data:
        data = data.replace(OLD_CN, NEW_CN, 1)
        ok += 1
        print("  ✅ _faceVariantscn 改为动态取键（未转义）")
    else:
        print("  ❌ _faceVariantscn —— 未匹配")

    # 3) cheatsFaceStyle 的 _faceStylescn 也做同样处理
    import re
    m = re.search(r"<<set _faceStylescn = \[[^\]]*\]>>", data)
    if m:
        print(f"  发现 _faceStylescn: {m.group(0)[:120]}")
        data = data.replace(
            m.group(0),
            "<<set _faceStylescn = Object.keys(setup.faceStyleOptions)>>",
            1,
        )
        ok += 1
        print("  ✅ _faceStylescn 改为动态取键")
    else:
        print("  （未找到 _faceStylescn 硬编码）")

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"\n命中 {ok} 项")
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
