"""A03（第3轮）：剥离宏后，只检查 .twee 正文纯文本部分的英文。"""
import base64
import html
import io
import json
import re
import zipfile
from collections import Counter

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
CJK = re.compile(r"[\u4e00-\u9fff]")
SKIP_MODS = {"ModI18N", "ModLoaderGui", "ModLoader", "ModLoader DoL ImageLoaderHook"}

z = zipfile.ZipFile(APK)
g = html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", g, re.S)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1))

ALLOW = set("""
id url http https www png jpg jpeg gif webp svg js css json twee html txt md
api ok no yes true false null undefined nan px em rem vh vw deg
mod mods apk android ios pc npc npcs hd dlc ui gui
boot sidebar indexdb localstorage
""".split())


def strip_all(s):
    """剥离宏 + HTML 标签 + 注释，只留纯文本。"""
    s = re.sub(r"<<[^<>]*(?:<[^<>]*>[^<>]*)*>>", " ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"/\*.*?\*/", " ", s, flags=re.S)
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    return s


results = []
for idx, s in enumerate(parts):
    raw = base64.b64decode(re.sub(r"\s+", "", s))
    if raw[:2] != b"PK":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(raw))
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
        modname = bj.get("name", f"#{idx}")
    except Exception:
        continue
    if modname in SKIP_MODS:
        continue

    for n in zz.namelist():
        if not n.endswith(".twee"):
            continue
        try:
            txt = zz.read(n).decode("utf-8", "replace")
        except Exception:
            continue

        for line_no, line in enumerate(txt.split("\n"), 1):
            if not CJK.search(line):
                continue
            pure = strip_all(line)
            if len(CJK.findall(pure)) < 4:
                continue
            # 纯文本里还有英文单词吗
            words = re.findall(r"\b[A-Za-z]{3,}\b", pure)
            bad = [w for w in words if w.lower() not in ALLOW]
            if not bad:
                continue
            results.append({
                "mod": modname, "file": n, "line": line_no,
                "text": line.strip()[:240],
                "pure": pure.strip()[:200],
                "words": bad[:8],
            })

print("=" * 100)
print(f"命中 {len(results)} 行")
print("=" * 100)

by_mod = Counter(r["mod"] for r in results)
print("\n按模组:")
for mod, cnt in by_mod.most_common(25):
    print(f"  {cnt:>4}  {mod}")

print("\n" + "=" * 100)
print("明细（全部，最多 80 条）")
print("=" * 100)
for r in results[:80]:
    print(f"\n[{r['mod']}] {r['file']}:{r['line']}")
    print(f"  EN: {r['words']}")
    print(f"  纯文本: {r['pure']!r}")

with open(r"E:\TAML\_dol\work\_mod_cn_en3.txt", "w", encoding="utf-8") as f:
    for r in results:
        f.write(f"{r['mod']}\t{r['file']}\t{r['line']}\t{','.join(r['words'])}\t{r['pure']}\n")
print(f"\n已保存 _mod_cn_en3.txt（{len(results)} 行）")
