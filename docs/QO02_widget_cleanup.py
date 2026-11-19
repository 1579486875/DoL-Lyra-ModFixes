"""后处理：把被翻译破坏的 widget 名修复回来。

i18n 里有些条目会把标识符的一部分翻掉，例如：
  flesh_text -> f浅色_text   （flesh -> 浅色，保留了 f 和 _text）
  characteristics -> ch一个racteristics

BE_bake 的黑名单能挡住整条匹配的情况，但挡不住「子串替换」。
这里做最后一道兜底：扫描所有含非 ASCII 的 widget 名，尝试还原。

还原策略：
  1) 常见映射表（f浅色_text -> flesh_text 等）
  2) 把名字里的中文段替换成候选英文（用 vanilla 的 widget 名做字典）
"""
import html as H
import os
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
VANILLA = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"

# 已知的手工映射
MANUAL = {
    "f浅色_text": "flesh_text",
    "ch一个racteristics": "characteristics",
}


def vanilla_widgets():
    try:
        z = zipfile.ZipFile(VANILLA)
        g = H.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))
        return set(re.findall(r'<<widget\s+"([^"]+)"', g))
    except Exception:
        return set()


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    g = H.unescape(data)

    vnames = vanilla_widgets()

    bad = [n for n in re.findall(r'<<widget\s+"([^"]+)"', g) if re.search(r"[^\x00-\x7f]", n)]
    print(f"含非 ASCII 的 widget 名: {len(bad)}")

    fixed = 0
    for name in bad:
        target = MANUAL.get(name)
        if not target:
            # 用 vanilla 名字做模糊匹配：去掉名字里的中文，看能否对上
            ascii_part = re.sub(r"[^\x20-\x7e]", "", name)
            if not ascii_part:
                continue
            cands = [v for v in vnames if ascii_part in v or v in ascii_part]
            # 再用「长度相近」过滤
            cands = [v for v in cands if abs(len(v) - len(name)) <= 6]
            if len(cands) == 1:
                target = cands[0]
        if not target:
            print(f"  ⚠️ 无法还原: {name!r}")
            continue
        # 替换（兼容转义形态）
        for a, b in ((H.escape('<<widget "' + name + '">>', quote=False),
                      H.escape('<<widget "' + target + '">>', quote=False)),
                     ('<<widget "' + name + '">>', '<<widget "' + target + '">>')):
            if a in data:
                data = data.replace(a, b)
                # 也替换关闭标签附近的调用
                data = data.replace("<<" + name + ">>", "<<" + target + ">>")
                fixed += 1
                print(f"  ✅ {name!r} -> {target!r}")
                break

    print(f"\n修复 {fixed} 处")

    if data != H.unescape(data) or fixed:
        open(HTML, "wb").write(data.encode("utf-8"))
        print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")

    # 校验
    g2 = H.unescape(data)
    names = re.findall(r'<<widget\s+"([^"]+)"', g2)
    bad2 = [n for n in names if re.search(r"[^\x00-\x7f]", n)]
    print(f"\n=== 校验 ===")
    print(f"  widget 总数 {len(names)}，含非 ASCII {len(bad2)}")
    if bad2:
        print(f"  ❌ {bad2}")
    else:
        print("  ✅ 全部 ASCII")
    return 0


if __name__ == "__main__":
    sys.exit(main())
