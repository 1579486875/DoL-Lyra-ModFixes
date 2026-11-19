"""修复 SF01 造成的 widget 嵌套（兼容 HTML 转义形态）。

index.html 里宏是 &lt;&lt;widget ... &gt;&gt;，引号是原样的。
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")

    # 用转义形态匹配 variablesStatic widget
    pat = re.compile(r'(&lt;&lt;widget "variablesStatic"&gt;&gt;)(.*?)(&lt;&lt;/widget&gt;&gt;)', re.S)
    m = pat.search(data)
    if not m:
        print("❌ 找不到 variablesStatic widget（转义形态）")
        # 诊断
        i = data.find('variablesStatic')
        print(f"  variablesStatic 首次出现 @{i}")
        print(f"  上下文: {data[max(0,i-120):i+120]!r}")
        return 1

    head, body, tail = m.group(1), m.group(2), m.group(3)
    print(f"variablesStatic 长度: {len(body)}")

    # 检查内部是否有 wTimerProgress widget
    wt_pat = re.compile(r'&lt;&lt;widget "wTimerProgress"&gt;&gt;.*?&lt;&lt;/widget&gt;&gt;', re.S)
    found = wt_pat.findall(body)
    print(f"  内部 wTimerProgress widget: {len(found)} 个")

    if not found:
        print("  （无需移除，可能已修）")
        # 但仍要检查是否真有嵌套
        nested = len(re.findall(r'&lt;&lt;widget\b', body))
        print(f"  但内部还有 {nested} 个 widget 定义")
        if nested == 0:
            return 0

    # 移除
    new_body = wt_pat.sub("", body)
    removed = len(found)
    print(f"✅ 已移除 {removed} 个嵌套的 wTimerProgress")

    # 取出被移除的第一个，稍后插到 passage 级别
    wt_block = found[0] if found else ""

    data = data[:m.start()] + head + new_body + tail + data[m.end():]

    # 插到 variablesStatic 之后
    if wt_block and wt_block not in data:
        data = data.replace(tail, tail + "\n" + wt_block, 1)
        print("✅ 已插到 variablesStatic 之后")

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")

    # 校验
    g = H.unescape(data)
    print("\n=== 校验 ===")
    m2 = re.search(r'<<widget\s+"variablesStatic"\s*>>(.*?)<</widget>>', g, re.S)
    if m2:
        nested = len(re.findall(r'<<widget\b', m2.group(1)))
        print(f"  variablesStatic 内 widget: {nested}  {'✅' if nested == 0 else '❌'}")
        print(f"  长度: {len(m2.group(1))}")
    print(f"  wTimerProgress 定义: {len(re.findall(chr(60)*2 + 'widget \"wTimerProgress\"', g))}")

    # 再查其他 widget 是否也被插了嵌套
    print("\n=== 全库检查 widget 嵌套 ===")
    raw = open(HTML, "rb").read().decode("utf-8", "replace")
    bad = []
    for mm in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        pn = html.unescape(mm.group(1))
        b = html.unescape(mm.group(2))
        for w in re.finditer(r'<<widget\s+"([^"]+)"\s*>>(.*?)<</widget>>', b, re.S):
            if "<<widget" in w.group(2):
                bad.append((pn, w.group(1)))
    print(f"  嵌套 widget: {len(bad)}")
    for x in bad[:10]:
        print(f"    {x}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
