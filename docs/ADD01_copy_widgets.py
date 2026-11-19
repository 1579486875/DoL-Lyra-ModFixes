"""最终方案：构建时把 Widgets Wraith 的所有 widget 定义复制到 variablesStatic。

原理：Widgets Wraith 的注册流程存在不明中断，导致部分 widget 不注册。
      把它们复制到能正常注册的 variablesStatic，已注册的会报 "already exists"（无害），
      未注册的成功注册。
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

MARK = "/* ===== copied-wraith-widgets (build-time fallback) ===== */"


def extract_all_widgets(text):
    """提取所有顶层 <<widget ...>>...</widget>> 块。"""
    out = []
    i = 0
    while True:
        m = re.search(r'<<widget\s+"([^"]+)"\s*>>', text[i:])
        if not m:
            break
        start = i + m.start()
        name = m.group(1)
        j = i + m.end()
        depth = 1
        while j < len(text) and depth > 0:
            if text.startswith("<<widget ", j):
                depth += 1
                j += 9
            elif text.startswith("<</widget>>", j):
                depth -= 1
                j += 11
                if depth == 0:
                    break
            else:
                j += 1
        out.append((name, text[start:j]))
        i = j
    return out


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")

    # 1) 移除运行时补注册器
    for pat_s in [
        r"&lt;&lt;script&gt;&gt;\s*\(function \(\) \{\s*var DONE = false.*?&lt;&lt;/script&gt;&gt;",
        r"<<script>>\s*\(function \(\) \{\s*var DONE = false.*?<</script>>",
    ]:
        p = re.compile(pat_s, re.S)
        while p.search(data):
            data = p.sub("", data, 1)
    print("✅ 已回滚运行时补注册器")

    # 2) 提取 Widgets Wraith 的 widget
    m = re.search(r'<tw-passagedata[^>]*name="Widgets Wraith"[^>]*>(.*?)</tw-passagedata>', data, re.S)
    if not m:
        print("❌ 找不到 Widgets Wraith")
        return 1
    body = H.unescape(m.group(1))
    widgets = extract_all_widgets(body)
    print(f"  提取 {len(widgets)} 个 widget")

    # 3) 移除已有的复制块（幂等）
    if MARK in H.unescape(data):
        g = H.unescape(data)
        i = g.find(MARK)
        # 找到复制块的结尾（下一个 </widget>> 之后）
        j = g.find("<</widget>>", i)
        # 复制块是多个 widget 连续，找最后一个
        while True:
            k = g.find("<</widget>>", j + 11)
            if k < 0:
                break
            # 检查 k 到 k+200 之间是否还有 widget
            if "&lt;&lt;widget" in g[j + 11:k + 200] or "<<widget" in g[j + 11:k + 200]:
                j = k
            else:
                break
        # 简化：直接用正则删
        pat = re.compile(re.escape(MARK) + r".*?(?=</tw-passagedata>)", re.S)
        g = pat.sub("", g, count=1)
        data = H.escape(g, quote=False)
        print("  （已移除旧的复制块）")

    # 4) 构造复制块
    parts = [MARK]
    for name, blk in widgets:
        parts.append(blk)
    copy_block = "\n\n".join(parts) + "\n"

    # 5) 插到 variablesStatic 末尾
    VS_CLOSE = '&lt;&lt;/widget&gt;&gt;'
    vs = data.find('&lt;&lt;widget "variablesStatic"&gt;&gt;')
    if vs < 0:
        print("❌ 找不到 variablesStatic")
        return 1
    vc = data.find(VS_CLOSE, vs) + len(VS_CLOSE)
    data = data[:vc] + "\n" + H.escape(copy_block, quote=False) + data[vc:]
    print(f"✅ 已复制 {len(widgets)} 个 widget 到 variablesStatic")

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")

    # 校验
    g2 = H.unescape(data)
    for name in ["rngWraith", "wHunt", "wPersist", "wraithIntro", "wraith_pass", "possessedWord"]:
        n = len(re.findall(r'<<widget "' + re.escape(name) + r'"', g2))
        print(f"  {name}: {n} 处")
    return 0


if __name__ == "__main__":
    sys.exit(main())
