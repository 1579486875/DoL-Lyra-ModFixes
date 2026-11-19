"""A02（第2轮）：只扫 .twee 正文里的中英混杂，排除翻译表和代码字段。"""
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

# 明确的「技术标识」白名单（不翻译）
ALLOW = set("""
id url http https www png jpg jpeg gif webp svg js css json twee html txt md
api ok no yes true false null undefined nan px em rem vh vw deg
mod mods apk android ios pc npc npcs hd dlc ui gui
boot side load remote local storage indexdb localstorage
debug error warn info log
""".split())


def is_code_line(line):
    s = line.strip()
    if s.startswith("<<"):
        # 纯宏行（里面有中文可能是消息参数）
        if not re.search(r"[\u4e00-\u9fff]{8,}", s):
            return True
    # JSON/JS 字段
    if re.match(r'^\s*["\']?\w+["\']?\s*[:=]\s*["\']', s):
        if not re.search(r"[\u4e00-\u9fff]{8,}", s):
            return True
    # 注释
    if s.startswith("//") or s.startswith("/*") or s.startswith("*"):
        if not re.search(r"[\u4e00-\u9fff]{8,}", s):
            return True
    return False


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
            # 中文至少 6 个字符（正文行）
            cn_chars = len(CJK.findall(line))
            if cn_chars < 6:
                continue
            if is_code_line(line):
                continue
            words = re.findall(r"\b[A-Za-z]{3,}\b", line)
            if not words:
                continue
            bad = [w for w in words if w.lower() not in ALLOW]
            if not bad:
                continue
            results.append({
                "mod": modname, "file": n, "line": line_no,
                "text": line.strip()[:220], "words": bad[:8],
            })

print("=" * 100)
print(f"命中 {len(results)} 行（.twee 正文）")
print("=" * 100)

by_mod = Counter(r["mod"] for r in results)
print("\n按模组:")
for mod, cnt in by_mod.most_common(25):
    print(f"  {cnt:>4}  {mod}")

print("\n" + "=" * 100)
print("明细（前 50 条）")
print("=" * 100)
for r in results[:50]:
    print(f"\n[{r['mod']}] {r['file']}:{r['line']}")
    print(f"  EN: {r['words']}")
    print(f"  {r['text']!r}")

with open(r"E:\TAML\_dol\work\_mod_cn_en2.txt", "w", encoding="utf-8") as f:
    for r in results:
        f.write(f"{r['mod']}\t{r['file']}\t{r['line']}\t{','.join(r['words'])}\t{r['text']}\n")
print(f"\n已保存 _mod_cn_en2.txt（{len(results)} 行）")
