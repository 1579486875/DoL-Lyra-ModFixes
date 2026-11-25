# -*- coding: utf-8 -*-
"""对比原版/我们的 setup.handhelds 里 toothbrush / soap 的 folder 字段。"""
import re
import zipfile

APKS = [
    ("原版", r"E:\TAML\_dol\apk\对照-基础版-无美化.apk"),
    ("AU-F", r"E:\TAML\_dol\apk\对照-AU-F立绘版.apk"),
    ("我们", r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"),
]

KEYS = ["toothbrush", "soap", "toast", "rag", "sponge", "bodywash", "shampoo", "toothpaste"]


def extract_block(text, start):
    """从 start 处提取一个 {...} 块（含嵌套）。"""
    i = text.find("{", start)
    if i < 0:
        return None
    depth = 0
    j = i
    while j < len(text):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[i:j + 1]
        j += 1
    return None


for label, path in APKS:
    z = zipfile.ZipFile(path)
    h = z.read("assets/www/index.html").decode("utf-8", "replace")
    print("\n" + "=" * 62)
    print("【%s】" % label)
    print("=" * 62)
    for k in KEYS:
        # 在 handhelds 段内找
        idx = h.find("handhelds")
        found = None
        if idx >= 0:
            seg = h[idx:idx + 30000]
            m = re.search(r"(?:^|[{,\s])%s\s*:\s*\{" % re.escape(k), seg)
            if m:
                found = extract_block(seg, m.start())
        if not found:
            print("  %-12s ❌ 未找到" % k)
            continue
        folder = re.search(r"folder\s*:\s*[\"']([^\"']+)[\"']", found)
        print("  %-12s folder=%s   %s" % (
            k,
            folder.group(1) if folder else "**缺失**",
            found.replace("\n", " ")[:110]))
