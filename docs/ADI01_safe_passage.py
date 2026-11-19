"""稳妥版：新建独立 widget passage 承载 12 个注册失败的 widget。

关键：不动原 passage（重复定义报 already exists 但能注册）。
先备份 index。
"""
import html as H
import os
import re
import shutil
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
BACKUP = r"E:\TAML\_dol\work\index_modded6.bak.html"
NEW_PN = "Widgets Repair"

NEED = [
    "effectsWraith", "chastityBreakWraith", "apologyWraith", "rescueWraith",
    "ejacW", "ejaculation-wraith", "kissWraith", "wHunt", "wPersist",
    "exitWraith", "rngWraith", "rngWraithSocial", "wraithEventStreet",
    "wraithEventSewers", "wraithIntro", "wraithCaught",
]


def extract_widget(text, name):
    i = text.find(f'<<widget "{name}">>')
    if i < 0:
        return None
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
    return text[i:j]


def main():
    # 备份
    shutil.copy2(HTML, BACKUP)
    print(f"✅ 已备份到 {BACKUP}")

    data = open(HTML, "rb").read().decode("utf-8", "replace")

    # 移除已存在的新 passage
    pat_pn = re.compile(r'<tw-passagedata[^>]*name="' + re.escape(NEW_PN) + r'"[^>]*>.*?</tw-passagedata>', re.S)
    n_old = len(pat_pn.findall(data))
    if n_old:
        data = pat_pn.sub("", data)
        print(f"  移除旧 {NEW_PN} × {n_old}")

    # 提取 Widgets Wraith
    m = re.search(r'<tw-passagedata([^>]*)>(.*?)</tw-passagedata>', data, re.S)
    if not m:
        print("❌ 无 passage")
        return 1

    # 逐 passage 找
    body = None
    for mm in re.finditer(r'<tw-passagedata([^>]*)>(.*?)</tw-passagedata>', data, re.S):
        nm = re.search(r'name="([^"]+)"', mm.group(1))
        if nm and H.unescape(nm.group(1)) == "Widgets Wraith":
            body = H.unescape(mm.group(2))
            break
    if body is None:
        print("❌ 找不到 Widgets Wraith")
        return 1

    blocks = []
    missing = []
    for name in NEED:
        blk = extract_widget(body, name)
        if blk:
            blocks.append(blk)
        else:
            missing.append(name)
    print(f"  提取 {len(blocks)} 个 widget" + (f"（缺 {missing}）" if missing else ""))

    if not blocks:
        print("❌ 没提取到")
        return 1

    # 构造新 passage
    inner = "\n" + "\n\n".join(blocks) + "\n"
    pids = [int(x) for x in re.findall(r'<tw-passagedata[^>]*pid="(\d+)"', data)]
    new_pid = (max(pids) + 1) if pids else 1

    new_passage = (
        f'<tw-passagedata pid="{new_pid}" name="{NEW_PN}" tags="widget" '
        f'position="0,0" size="100,100">' + H.escape(inner, quote=False) + '</tw-passagedata>'
    )

    # 插到 storydata 之后第一个位置
    sm = re.search(r'<tw-storydata[^>]*>', data)
    data = data[:sm.end()] + "\n" + new_passage + data[sm.end():]
    print(f"✅ 已创建 {NEW_PN}（pid={new_pid}，{len(blocks)} 个 widget）")

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")

    # 校验
    raw2 = open(HTML, "rb").read().decode("utf-8", "replace")
    print("\n=== 校验 ===")
    print(f"  passage 总数: {len(re.findall(r'<tw-passagedata', raw2))}")
    print(f"  {NEW_PN} 存在: {NEW_PN in H.unescape(raw2)}")
    print(f"  Widgets Wraith 完好: {'Widgets Wraith' in H.unescape(raw2)}")
    g2 = H.unescape(raw2)
    for name in NEED[:4]:
        print(f"  {name}: {len(re.findall(chr(60)*2 + 'widget ' + chr(34) + re.escape(name) + chr(34), g2))} 处定义")
    return 0


if __name__ == "__main__":
    sys.exit(main())
