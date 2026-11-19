"""第 22 轮：保留宏做占位符，再比对 i18n。

关键：i18n 表的 f 是「带宏的原文」，如 "You feel <<his>> breath on your <<his>>."
      所以必须把宏替换成统一占位符再比对，不能直接剥离。
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
PH = "\u0001"   # 占位符


def load_items():
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
    return d.get("typeB", {}).get("TypeBInputStoryScript", [])


def norm(s):
    """归一化：宏 -> 占位符，压缩空白。"""
    s = re.sub(r"<<[^<>]*(?:<[^<>]*>[^<>]*)*>>", PH, s)
    s = re.sub(r"<[^>]+>", PH, s)      # HTML 标签也算占位
    s = re.sub(r"\s+", " ", s)
    return s.strip()


items = load_items()
print(f"i18n 条目 {len(items):,}")
keys_norm = set()
for it in items:
    f = it.get("f")
    if f:
        keys_norm.add(norm(f))
print(f"归一化键 {len(keys_norm):,}")

z = zipfile.ZipFile(APK)
raw = z.read("assets/www/index.html").decode("utf-8", "replace")

blocks = []
for m in re.finditer(r'<tw-passagedata([^>]*)>(.*?)</tw-passagedata>', raw, re.S):
    nm = re.search(r'name="([^"]+)"', m.group(1))
    if nm:
        blocks.append((html.unescape(nm.group(1)), html.unescape(m.group(2))))

print(f"passage {len(blocks)}")


def is_english(s):
    s2 = s.replace(PH, " ")
    s2 = s2.strip()
    if len(s2) < 10 or len(s2) > 500:
        return False
    words = re.findall(r"[A-Za-z][A-Za-z']+", s2)
    if len(words) < 3:
        return False
    if re.search(r"[\u4e00-\u9fff]", s2):
        return False
    if not re.fullmatch(r"[A-Za-z0-9\s.,!?;:'\"()\-–—…%$*/+&\[\]]+", s2):
        return False
    if re.search(r"[{}<>=$`\\]|=>|\bfunction\b|\bvar\b|\bconst\b|\blet\b|"
                 r"\breturn\b|\bundefined\b|\bthis\.|\boutput\.", s2):
        return False
    if re.search(r"\d\.\d\.\d|/|\.js\b|\.png\b", s2):
        return False
    return True


missing = []
scanned = 0
for pn, body in blocks:
    b = body
    b = re.sub(r"<script\b.*?</script>", " ", b, flags=re.S | re.I)
    b = re.sub(r"<style\b.*?</style>", " ", b, flags=re.S | re.I)
    b = re.sub(r"/\*.*?\*/", " ", b, flags=re.S)
    b = re.sub(r"<!--.*?-->", " ", b, flags=re.S)
    b = re.sub(r"//[^\n]*", " ", b)

    # 按段落切（不先剥宏）
    for sent in re.split(r"(?<=[.!?])\s+", b):
        s = sent.strip()
        if not is_english(s):
            continue
        scanned += 1
        if norm(s) not in keys_norm:
            missing.append((pn, s))

print(f"\n扫描 {scanned:,} 句，漏翻 {len(missing)} 句，涉及 {len(set(p for p, _ in missing))} passage")

by_p = Counter(pn for pn, _ in missing)
print("\nTop 20 passage:")
for pn, c in by_p.most_common(20):
    print(f"  {c:>4}  {pn}")

print("\n全部漏翻:")
for pn, s in missing[:60]:
    print(f"  [{pn}] {s[:130]!r}")

with open(r"E:\TAML\_dol\work\_missing_tr3.txt", "w", encoding="utf-8") as f:
    for pn, s in missing:
        f.write(f"{pn}\t{s}\n")
    f.write(f"# total {len(missing)}\n")

print(f"\n已保存 _missing_tr3.txt（{len(missing)} 条）")
sys.exit(1 if missing else 0)
