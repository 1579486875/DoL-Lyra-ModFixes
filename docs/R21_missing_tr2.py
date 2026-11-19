"""第 21 轮：区分「代码注释」与「玩家可见正文」，只修真漏翻。

方法：
  1. 剥离 <script> / /* */ / //  → 去掉代码
  2. 多轮剥离 <<...>> 宏
  3. 剩下的就是 passage 纯正文 → 扫英文
"""
import html
import json
import os
import re
import sys
import zipfile
from collections import Counter

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
I18N = r"E:\TAML\_dol\work\i18n_dict.json"


def load_keys():
    import pickle
    cache = I18N + ".pkl"
    d = None
    try:
        if os.path.exists(cache) and os.path.getmtime(cache) > os.path.getmtime(I18N):
            with open(cache, "rb") as f:
                d = pickle.load(f)
    except Exception:
        d = None
    if d is None:
        with open(I18N, "r", encoding="utf-8") as f:
            d = json.load(f)
    items = d.get("typeB", {}).get("TypeBInputStoryScript", [])
    return set(it["f"].strip() for it in items if it.get("f"))


def strip_macros(s):
    prev = None
    for _ in range(8):
        if s == prev:
            break
        prev = s
        s = re.sub(r"<<[^<>]*(?:<[^<>]*>[^<>]*)*>>", " ", s)
    return s


def is_english(s):
    s = s.strip()
    if len(s) < 10 or len(s) > 500:
        return False
    words = re.findall(r"[A-Za-z][A-Za-z']+", s)
    if len(words) < 3:
        return False
    if re.search(r"[\u4e00-\u9fff]", s):
        return False
    if not re.fullmatch(r"[A-Za-z0-9\s.,!?;:'\"()\-–—…%$*/+&\[\]]+", s):
        return False
    # 排除代码特征
    if re.search(r"[{}<>=$`\\]|=>|\bfunction\b|\bvar\b|\bconst\b|\blet\b|"
                 r"\breturn\b|\bundefined\b|\bnull\b|\bthis\.|\boutput\.", s):
        return False
    # 排除版本号/路径
    if re.search(r"\d\.\d\.\d|/|\.js\b|\.png\b|\.txt\b", s):
        return False
    return True


keys = load_keys()
print(f"i18n 键 {len(keys):,}")

z = zipfile.ZipFile(APK)
raw = z.read("assets/www/index.html").decode("utf-8", "replace")

blocks = []
for m in re.finditer(r'<tw-passagedata([^>]*)>(.*?)</tw-passagedata>', raw, re.S):
    nm = re.search(r'name="([^"]+)"', m.group(1))
    if nm:
        blocks.append((html.unescape(nm.group(1)), html.unescape(m.group(2))))

print(f"passage {len(blocks)}")

missing = []
scanned = 0
for pn, body in blocks:
    b = body
    # 1) 去 script
    b = re.sub(r"<script\b.*?</script>", " ", b, flags=re.S | re.I)
    b = re.sub(r"<style\b.*?</style>", " ", b, flags=re.S | re.I)
    # 2) 去注释
    b = re.sub(r"/\*.*?\*/", " ", b, flags=re.S)
    b = re.sub(r"<!--.*?-->", " ", b, flags=re.S)
    b = re.sub(r"//[^\n]*", " ", b)
    # 3) 去宏（多轮）
    b = strip_macros(b)
    # 4) 去 HTML 标签
    b = re.sub(r"<[^>]+>", " ", b)

    for sent in re.split(r"(?<=[.!?])\s+", b):
        s = sent.strip()
        if not is_english(s):
            continue
        scanned += 1
        if s not in keys:
            missing.append((pn, s))

print(f"\n扫描 {scanned:,} 句，漏翻 {len(missing)} 句，涉及 {len(set(p for p, _ in missing))} passage")

by_p = Counter(pn for pn, _ in missing)
print("\nTop 20 passage:")
for pn, c in by_p.most_common(20):
    print(f"  {c:>4}  {pn}")

print("\n前 40 条:")
for pn, s in missing[:40]:
    print(f"  [{pn}] {s[:120]!r}")

with open(r"E:\TAML\_dol\work\_missing_tr2.txt", "w", encoding="utf-8") as f:
    for pn, s in missing:
        f.write(f"{pn}\t{s}\n")

print(f"\n已保存 _missing_tr2.txt（{len(missing)} 条）")
sys.exit(1 if missing else 0)
