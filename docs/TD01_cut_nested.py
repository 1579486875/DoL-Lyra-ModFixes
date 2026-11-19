"""精确剪切：把 variablesStatic 里误插的 wTimerProgress widget 移出去。"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")

    WIDGET_OPEN = '&lt;&lt;widget "wTimerProgress"&gt;&gt;'
    WIDGET_CLOSE = '&lt;&lt;/widget&gt;&gt;'

    # 1) 找到 variablesStatic 的起点
    vs_start = data.find('&lt;&lt;widget "variablesStatic"&gt;&gt;')
    if vs_start < 0:
        print("❌ 找不到 variablesStatic")
        return 1

    # 2) 在 variablesStatic 之后找 wTimerProgress
    wt_start = data.find(WIDGET_OPEN, vs_start)
    if wt_start < 0:
        print("（variablesStatic 之后没有 wTimerProgress）")
        return 0

    # 3) 从 wTimerProgress 起点找它的 </widget>>
    wt_end = data.find(WIDGET_CLOSE, wt_start)
    if wt_end < 0:
        print("❌ wTimerProgress 没有闭合")
        return 1
    wt_end += len(WIDGET_CLOSE)

    # 4) 判断它是否真的在 variablesStatic 内部
    #    variablesStatic 的 </widget>> 应该在 wTimerProgress 之后（如果嵌套）或之前
    vs_close_search = data.find(WIDGET_CLOSE, vs_start)
    nested = (vs_close_search == wt_end)  # variablesStatic 的闭合正好是 wTimerProgress 的闭合 → 说明嵌套

    print(f"wTimerProgress 位置: {wt_start} ~ {wt_end}")
    print(f"variablesStatic 首个 </widget>> 位置: {vs_close_search}")
    print(f"判定嵌套: {nested}")

    block = data[wt_start:wt_end]
    print(f"块长度: {len(block)}")
    print(f"块内容: {block[:150]!r}...")

    # 5) 剪切
    data = data[:wt_start] + data[wt_end:]
    print("✅ 已从原位置剪切")

    # 6) 插到 variablesStatic 整个 widget 结束之后
    #    重新找 variablesStatic 的闭合
    vs_start = data.find('&lt;&lt;widget "variablesStatic"&gt;&gt;')
    vs_close = data.find(WIDGET_CLOSE, vs_start)
    if vs_close < 0:
        print("❌ 找不到 variablesStatic 闭合")
        return 1
    vs_close += len(WIDGET_CLOSE)

    data = data[:vs_close] + "\n" + block + data[vs_close:]
    print("✅ 已插到 variablesStatic 之后")

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")

    # 7) 校验
    g = H.unescape(data)
    print("\n=== 校验 ===")
    m = re.search(r'<<widget\s+"variablesStatic"\s*>>(.*?)<</widget>>', g, re.S)
    if m:
        nested = len(re.findall(r'<<widget\b', m.group(1)))
        print(f"  variablesStatic 内 widget: {nested}  {'✅' if nested == 0 else '❌'}")
        print(f"  长度: {len(m.group(1))}")
    print(f"  wTimerProgress 定义: {len(re.findall(chr(60)*2 + 'widget \"wTimerProgress\"', g))}")

    # 8) 全库 widget 嵌套检查
    print("\n=== 全库 widget 嵌套 ===")
    raw = open(HTML, "rb").read().decode("utf-8", "replace")
    bad = []
    for mm in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        pn = H.unescape(mm.group(1))
        b = H.unescape(mm.group(2))
        for w in re.finditer(r'<<widget\s+"([^"]+)"\s*>>(.*?)<</widget>>', b, re.S):
            if "<<widget" in w.group(2):
                bad.append((pn, w.group(1)))
    print(f"  嵌套 widget: {len(bad)}")
    for x in bad[:10]:
        print(f"    {x}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
