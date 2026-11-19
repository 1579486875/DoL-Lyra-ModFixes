"""第 20 轮：零错误层③ 翻译 —— 找 index 里漏翻的英文句子。

DoL 的 i18n 是「英文原文 -> 中文」映射，所以「键」是英文原文。
判据：index 里出现的英文句子，有多少不在 i18n 表里（= 漏翻）。
"""
import html
import json
import os
import re
import sys
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
I18N = r"E:\TAML\_dol\work\i18n_dict.json"


def load_i18n(p):
    """加载 i18n，返回英文原文集合（小写化后）。"""
    import pickle
    cache = p + ".pkl"
    d = None
    try:
        if os.path.exists(cache) and os.path.getmtime(cache) > os.path.getmtime(p):
            with open(cache, "rb") as f:
                d = pickle.load(f)
    except Exception:
        d = None
    if d is None:
        with open(p, "r", encoding="utf-8") as f:
            d = json.load(f)
    items = d.get("typeB", {}).get("TypeBInputStoryScript", [])
    keys = set()
    for it in items:
        f = it.get("f")
        if f:
            keys.add(f.strip())
    return keys, len(items)


print("加载 i18n ...")
keys, n = load_i18n(I18N)
print(f"  {n:,} 条，去重后 {len(keys):,} 个英文原文")

z = zipfile.ZipFile(APK)
raw = z.read("assets/www/index.html").decode("utf-8", "replace")
g = html.unescape(raw)

# 只取 passage 内容
blocks = []
for m in re.finditer(r'<tw-passagedata([^>]*)>(.*?)</tw-passagedata>', raw, re.S):
    nm = re.search(r'name="([^"]+)"', m.group(1))
    if nm:
        blocks.append((html.unescape(nm.group(1)), html.unescape(m.group(2))))

print(f"  {len(blocks)} passage")

# 过滤：只保留「像英文句子」的文本
def is_english_sentence(s):
    s = s.strip()
    if len(s) < 12 or len(s) > 400:
        return False
    # 必须有至少 3 个英文单词
    words = re.findall(r"[A-Za-z][A-Za-z']+", s)
    if len(words) < 3:
        return False
    # 不能含中文
    if re.search(r"[\u4e00-\u9fff]", s):
        return False
    # 必须是纯 ASCII 可见字符 + 常见标点
    if not re.fullmatch(r"[A-Za-z0-9\s.,!?;:'\"()\-–—…%$*/+&\[\]]+", s):
        return False
    # 不能是代码特征
    if re.search(r"[{}<>=$`]|=>|function|var |const |let ", s):
        return False
    return True


print("\n" + "=" * 88)
print("扫描每个 passage 的英文句子")
print("=" * 88)

missing = []
scanned = 0
for pn, body in blocks:
    # 剥离宏和 HTML
    b = re.sub(r"<<[^<>]*(?:<[^<>]*>[^<>]*)*>>", " ", body)
    b = re.sub(r"<[^>]+>", " ", b)
    b = re.sub(r"/\*.*?\*/", " ", b, flags=re.S)
    b = re.sub(r"//[^\n]*", " ", b)
    # 按句末标点切
    for sent in re.split(r"(?<=[.!?])\s+", b):
        s = sent.strip()
        if not is_english_sentence(s):
            continue
        scanned += 1
        if s not in keys:
            missing.append((pn, s))

print(f"  扫描到 {scanned:,} 个英文句子")
print(f"  不在 i18n 表里的: {len(missing)} 个")

# 按 passage 聚合
from collections import Counter, defaultdict
by_p = Counter(pn for pn, _ in missing)
print(f"  涉及 {len(by_p)} 个 passage")
print("\n  Top 15 passage:")
for pn, c in by_p.most_common(15):
    print(f"    {c:>4}  {pn}")

print("\n  前 20 条漏翻样例:")
for pn, s in missing[:20]:
    print(f"    [{pn}] {s[:110]!r}")

# 保存
with open(r"E:\TAML\_dol\work\_missing_tr.txt", "w", encoding="utf-8") as f:
    for pn, s in missing:
        f.write(f"{pn}\t{s}\n")
print(f"\n  已保存到 _missing_tr.txt")

sys.exit(1 if missing else 0)
