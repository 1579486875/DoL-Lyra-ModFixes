"""F06（第6轮）：扫中文正文里的英文单词（玩家可见文本，catboy 类）。"""
import html as H
import re
import zipfile
from collections import Counter, defaultdict

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
raw = zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace")
g = H.unescape(raw)
TICK = chr(96)

PASSAGES = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
    PASSAGES[m.group(1)] = H.unescape(m.group(2))

# 允许的英文（技术标识 / 专有名词 / 已在映射表里的 key）
ALLOW = set("""
id url http https www png jpg jpeg gif webp svg js css json twee html xml txt md
api ok no yes true false null undefined nan px em rem vh vw deg
mod mods apk android ios pc npc npcs hd dlc ui gui dpi
boot sideload remote local indexdb localstorage
sugarCube del do l loli lyra maple birch modloader tweereplacer
wtf gps dna ok tv cd usb ai
""".split())

# 全角 / 半角中文标点
result = []
for pname, body in PASSAGES.items():
    # 逐行
    for line_no, line in enumerate(body.split("\n"), 1):
        if not re.search(r"[\u4e00-\u9fff]", line):
            continue
        # 剥离宏、HTML 标签
        stripped = re.sub(r"<<[^<>]*(?:<[^<>]*>[^<>]*)*>>", " ", line)
        stripped = re.sub(r"<[^>]+>", " ", stripped)
        stripped = re.sub(r"/\*.*?\*/", " ", stripped)
        if len(re.findall(r"[\u4e00-\u9fff]", stripped)) < 4:
            continue
        # 找英文单词
        for m in re.finditer(r"\b([A-Za-z][A-Za-z'\-]{2,})\b", stripped):
            w = m.group(1)
            if w.lower() in ALLOW:
                continue
            if len(w) < 3:
                continue
            result.append((pname, line_no, w, stripped.strip()[:180]))

print("=" * 100)
print(f"中文正文里的英文单词: {len(result)} 处")
print("=" * 100)

# 按词聚合
by_word = Counter(r[2] for r in result)
print("\n出现最多的 40 个词:")
for w, c in by_word.most_common(40):
    print(f"  {c:>4}x {w!r}")

# 按模组/passage 聚合
by_passage = Counter(r[0] for r in result)
print("\n涉及最多的 20 个 passage:")
for p, c in by_passage.most_common(20):
    print(f"  {c:>4}  {p}")

print("\n" + "=" * 100)
print("明细（前 40 条）")
print("=" * 100)
for pname, line_no, w, txt in result[:40]:
    print(f"\n[{pname}]:{line_no}  EN={w!r}")
    print(f"  {txt!r}")

with open(r"E:\TAML\_dol\work\_cn_en_words.txt", "w", encoding="utf-8") as f:
    for pname, line_no, w, txt in result:
        f.write(f"{pname}\t{line_no}\t{w}\t{txt}\n")
print(f"\n已保存 _cn_en_words.txt")
