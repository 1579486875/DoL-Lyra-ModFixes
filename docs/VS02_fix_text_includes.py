"""修「文本字段英文子串判断」在中文值下失效的问题。

策略：保留原英文判断，追加中文判断：
    x.includes("metal")  ->  (x.includes("metal") || x.includes("金属"))
猜错中文也无害（只是多一个恒假的 OR）。

只处理 vanilla 有、modded 完全消失的判断（说明值已中文化）。
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

# 英文 -> 中文候选（英文串的翻译可能形态）
ZH = {
    "metal": ["金属"],
    "pale": ["苍白"],
    "locker": ["储物柜", "柜"],
    "some orphan": ["某个孤儿"],
    "gecko": ["壁虎"],
    "vivaldi": ["维瓦尔第"],
    "windows phone": ["windows phone"],
}

# 形如 (x.includes("en")) 的判断
FULL = r'([\w$\.\[\]]+)\s*\.\s*includes\(\s*["\']{en}["\']\s*\)'


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    total = 0

    for en, zh_list in ZH.items():
        pat = re.compile(FULL.format(en=re.escape(en)))
        hits = list(pat.finditer(data))
        if not hits:
            continue
        n = 0
        out = []
        last = 0
        for m in hits:
            obj = m.group(1)
            tail = data[m.end():m.end() + 120]
            # 已经兼容过就跳过
            if any(f'{obj}.includes("{z}")' in tail for z in zh_list):
                continue
            extra = " || ".join(f'{obj}.includes("{z}")' for z in zh_list)
            rep = f'({obj}.includes("{en}") || {extra})'
            out.append(data[last:m.start()])
            out.append(rep)
            last = m.end()
            n += 1
        if n:
            out.append(data[last:])
            data = "".join(out)
            total += n
            print(f"  ✅ {en!r} -> +{zh_list}  ({n} 处)")

    if total:
        open(HTML, "wb").write(data.encode("utf-8"))
        print(f"\n合计 {total} 处，写出 {HTML}")
    else:
        print("\n（无改动）")

    # 校验
    g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
    print("\n=== 校验 ===")
    for en in ZH:
        n = len(re.findall(r'\.\s*includes\(\s*["\']' + re.escape(en) + r'["\']\s*\)', g))
        print(f"  {en!r}: {n} 处")
    return 0


if __name__ == "__main__":
    sys.exit(main())
