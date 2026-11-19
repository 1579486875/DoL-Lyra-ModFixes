"""挪移剩余 4 个 MISSING widget（第二处中断）。"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

MOVE = ["wraithEventStreet", "wraithEventSewers", "wraithIntro", "wraithCaught"]


def extract_widget(text, name):
    i = text.find(f'<<widget "{name}">>')
    if i < 0:
        return None
    start = i
    j = i + len(f'<<widget "{name}">>')
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
    return text[start:j]


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    m = re.search(r'<tw-passagedata[^>]*name="Widgets Wraith"[^>]*>(.*?)</tw-passagedata>', data, re.S)
    if not m:
        print("❌ 找不到 Widgets Wraith")
        return 1

    body = H.unescape(m.group(1))
    blocks = []
    for name in MOVE:
        blk = extract_widget(body, name)
        if blk:
            blocks.append((name, blk))
    print(f"  提取 {len(blocks)} 个: {[b[0] for b in blocks]}")

    if not blocks:
        print("（已挪完）")
        return 0

    for name, blk in blocks:
        body = body.replace(blk, "", 1)

    data = data[:m.start(1)] + H.escape(body, quote=False) + data[m.end(1):]

    tail = "\n\n" + "\n\n".join(blk for _, blk in blocks) + "\n"
    VS_CLOSE = '&lt;&lt;/widget&gt;&gt;'
    vs = data.find('&lt;&lt;widget "variablesStatic"&gt;&gt;')
    vc = data.find(VS_CLOSE, vs) + len(VS_CLOSE)
    data = data[:vc] + H.escape(tail, quote=False) + data[vc:]
    print(f"✅ 已追加到 variablesStatic")

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
