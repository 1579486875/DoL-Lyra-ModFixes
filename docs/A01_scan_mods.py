"""A01（第1轮）：扫全部 58 个模组 zip 里「中文文本中嵌的英文」。

判据：
  - 一个字符串里同时含中文和英文单词
  - 英文部分不是技术标识（变量名/宏/路径/defName）
  - 英文部分长度 >= 3 且是完整单词
"""
import base64
import html
import io
import json
import re
import zipfile
from collections import Counter, defaultdict

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
CJK = re.compile(r"[\u4e00-\u9fff]")
# 允许的英文（技术标识）
ALLOW = set("""
id url http https www png jpg gif webp js css json twee html txt md
api css svg mp3 ogg wav mp4 webm
ok no yes true false null undefined nan
px em rem vh vw deg
""".split())

z = zipfile.ZipFile(APK)
g = html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))

m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", g, re.S)
if not m:
    print("❌ 无 modDataValueZipList")
    raise SystemExit(1)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1))
print(f"模组 zip {len(parts)} 个\n")

# 只扫「玩家可见」的文件
SCAN_EXT = (".twee", ".js", ".json", ".css", ".html", ".txt", ".md")

results = []
for idx, s in enumerate(parts):
    raw = base64.b64decode(re.sub(r"\s+", "", s))
    if raw[:2] != b"PK":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(raw))
    except Exception:
        continue
    try:
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
        modname = bj.get("name", f"#{idx}")
    except Exception:
        modname = f"#{idx}"

    for n in zz.namelist():
        if not n.endswith(SCAN_EXT):
            continue
        try:
            txt = zz.read(n).decode("utf-8", "replace")
        except Exception:
            continue

        # 逐行扫：含中文 + 含英文单词
        for line_no, line in enumerate(txt.split("\n"), 1):
            if not CJK.search(line):
                continue
            # 找英文单词（>=3 字母）
            words = re.findall(r"\b[A-Za-z]{3,}\b", line)
            if not words:
                continue
            bad = [w for w in words if w.lower() not in ALLOW]
            if not bad:
                continue
            # 排除纯代码行（<<set ...>> 之类）
            if re.match(r"^\s*<<(set|run|script|if|for|switch)\b", line):
                # 但如果里面有中文正文，也可能是问题
                if not re.search(r"[\u4e00-\u9fff]{6,}", line):
                    continue
            results.append({
                "mod": modname, "file": n, "line": line_no,
                "text": line.strip()[:200], "words": bad[:6]
            })

print("=" * 100)
print(f"命中 {len(results)} 行")
print("=" * 100)

# 按模组聚合
by_mod = Counter(r["mod"] for r in results)
for mod, cnt in by_mod.most_common(20):
    print(f"  {cnt:>4}  {mod}")

print("\n" + "=" * 100)
print("明细（前 60 条）")
print("=" * 100)
for r in results[:60]:
    print(f"\n[{r['mod']}] {r['file']}:{r['line']}")
    print(f"  英文: {r['words']}")
    print(f"  文本: {r['text']!r}")

with open(r"E:\TAML\_dol\work\_mod_cn_en.txt", "w", encoding="utf-8") as f:
    for r in results:
        f.write(f"{r['mod']}\t{r['file']}\t{r['line']}\t{','.join(r['words'])}\t{r['text']}\n")
print(f"\n已保存 _mod_cn_en.txt（{len(results)} 行）")
