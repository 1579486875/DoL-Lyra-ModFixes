"""F07（第7轮）：精确判据 —— 中文紧邻英文（catboy 类），排除代码。"""
import html as H
import json
import re
import zipfile
from collections import Counter

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
raw = zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace")
g = H.unescape(raw)
TICK = chr(96)

PASSAGES = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
    PASSAGES[m.group(1)] = H.unescape(m.group(2))

# 更可靠地剥离宏：用状态机
def strip_macros(text):
    out = []
    i = 0
    L = len(text)
    while i < L:
        j = text.find("<<", i)
        if j < 0:
            out.append(text[i:])
            break
        out.append(text[i:j])
        # 跳过 <<-- 注释 -->>
        if text.startswith("<<--", j):
            k = text.find("-->>", j + 4)
            i = k + 4 if k > 0 else L
            continue
        k = text.find(">>", j + 2)
        i = k + 2 if k > 0 else L
    return "".join(out)


ALLOW = set("""
id url http https www png jpg jpeg gif webp svg js css json twee html xml txt md
api ok no yes true false null undefined nan px em rem vh vw deg
mod mods apk android ios pc npc npcs hd dlc ui gui dpi
cm kg ml ml l bmi gps dna tv cd usb ai
""".split())

result = []
for pname, body in PASSAGES.items():
    for line_no, line in enumerate(body.split("\n"), 1):
        if not re.search(r"[\u4e00-\u9fff]", line):
            continue
        pure = strip_macros(line)
        pure = re.sub(r"<[^>]+>", " ", pure)
        if len(re.findall(r"[\u4e00-\u9fff]", pure)) < 2:
            continue
        # 找「中文 + 英文单词 + 中文」或「中文 + 英文单词 + 结束」
        for m in re.finditer(r"[\u4e00-\u9fff]([A-Za-z][A-Za-z'\-]{2,})[\u4e00-\u9fff]", pure):
            w = m.group(1)
            if w.lower() in ALLOW:
                continue
            result.append((pname, line_no, w, pure.strip()[:200], "前后中文"))
        # 「中文 + 英文 + 标点/结束」
        for m in re.finditer(r"[\u4e00-\u9fff]([A-Za-z][A-Za-z'\-]{2,})[。，！？；\s]", pure):
            w = m.group(1)
            if w.lower() in ALLOW:
                continue
            result.append((pname, line_no, w, pure.strip()[:200], "中文+英文+标点"))

print("=" * 100)
print(f"精确命中: {len(result)} 处")
print("=" * 100)

by_word = Counter(r[2] for r in result)
print("\n按词聚合（前 40）:")
for w, c in by_word.most_common(40):
    print(f"  {c:>4}x {w!r}")

by_passage = Counter(r[0] for r in result)
print("\n按 passage（前 15）:")
for p, c in by_passage.most_common(15):
    print(f"  {c:>4}  {p}")

print("\n" + "=" * 100)
print("明细（前 50 条）")
print("=" * 100)
for pname, line_no, w, txt, why in result[:50]:
    print(f"\n[{pname}]:{line_no}  EN={w!r}  ({why})")
    print(f"  {txt!r}")

with open(r"E:\TAML\_dol\work\_cn_en_precise.txt", "w", encoding="utf-8") as f:
    for pname, line_no, w, txt, why in result:
        f.write(f"{pname}\t{line_no}\t{w}\t{why}\t{txt}\n")
print(f"\n已保存 _cn_en_precise.txt")
