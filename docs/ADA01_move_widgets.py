"""回滚运行时补注册器，改用构建时挪移。

方案：把 Widgets Wraith 里注册失败的那批 widget（effectsWraith ~ rngWraithSocial）
      剪切出来，追加到 Widgets variablesStatic 的末尾（那里注册正常）。
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

# 需要挪移的 widget（从 probe 结果：第 14~28 个 MISSING）
MOVE = [
    "effectsWraith", "chastityBreakWraith", "apologyWraith", "rescueWraith",
    "ejacW", "ejaculation-wraith", "kissWraith", "wHunt", "wPersist",
    "exitWraith", "rngWraith", "rngWraithSocial",
]


def extract_widget(text, name):
    """提取 <<widget "name">>...</widget>> 的完整块。"""
    i = text.find(f'<<widget "{name}">>')
    if i < 0:
        return None, -1, -1
    start = i
    j = i + len(f'<<widget "{name}">>')
    depth = 1
    while j < len(text) and depth > 0:
        if text.startswith("<<widget ", j):
            depth += 1
            j += 9
        elif text.startswith("<</widget>>", j):
            depth -= 1
            if depth == 0:
                j += 11
                break
            j += 11
        else:
            j += 1
    return text[start:j], start, j


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")

    # 1) 移除旧补注册器
    for pat_s in [
        r"&lt;&lt;script&gt;&gt;\s*\(function \(\) \{\s*var DONE = false.*?&lt;&lt;/script&gt;&gt;",
        r"<<script>>\s*\(function \(\) \{\s*var DONE = false.*?<</script>>",
    ]:
        p = re.compile(pat_s, re.S)
        while p.search(data):
            data = p.sub("", data, 1)
    print("✅ 已回滚补注册器")

    # 2) 定位 Widgets Wraith passage（转义形态）
    g = H.unescape(data)
    # 找 passage 边界（在原始转义文本里操作）
    m = re.search(r'<tw-passagedata[^>]*name="Widgets Wraith"[^>]*>(.*?)</tw-passagedata>', data, re.S)
    if not m:
        print("❌ 找不到 Widgets Wraith")
        return 1

    body_esc = m.group(1)
    body = H.unescape(body_esc)
    print(f"  Widgets Wraith 长度 {len(body):,}")

    # 3) 提取要挪的 widget
    blocks = []
    for name in MOVE:
        blk, s, e = extract_widget(body, name)
        if blk:
            blocks.append((name, blk))
    print(f"  提取到 {len(blocks)} 个 widget")

    # 4) 从 body 里删除
    for name, blk in blocks:
        body = body.replace(blk, "", 1)
    print(f"  删除后长度 {len(body):,}")

    # 5) 写回 Widgets Wraith
    data = data[:m.start(1)] + H.escape(body, quote=False) + data[m.end(1):]

    # 6) 追加到 Widgets variablesStatic 末尾
    tail = "\n\n" + "\n\n".join(blk for _, blk in blocks) + "\n"
    VS_CLOSE = '&lt;&lt;/widget&gt;&gt;'
    vs = data.find('&lt;&lt;widget "variablesStatic"&gt;&gt;')
    if vs < 0:
        print("❌ 找不到 variablesStatic")
        return 1
    vc = data.find(VS_CLOSE, vs) + len(VS_CLOSE)
    data = data[:vc] + H.escape(tail, quote=False) + data[vc:]
    print(f"✅ 已把 {len(blocks)} 个 widget 追加到 variablesStatic")

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")

    # 校验
    g2 = H.unescape(data)
    print("\n=== 校验 ===")
    for name in MOVE:
        n = len(re.findall(r'<<widget "' + re.escape(name) + r'"', g2))
        print(f"  {name}: {n} 处定义")
    return 0


if __name__ == "__main__":
    sys.exit(main())
