"""第 24 轮：最严格判据 —— 只找「完整英文句子」（大写开头、有标点）。"""
import html
import re
import zipfile
from collections import Counter

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
raw = z.read("assets/www/index.html").decode("utf-8", "replace")

blocks = [(html.unescape(m.group(1)), m.group(2))
          for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S)]

CJK = re.compile(r"[\u4e00-\u9fff]")


def strip_all(s):
    s = html.unescape(s)
    for _ in range(3):
        s = re.sub(r"/\*.*?\*/", " ", s, flags=re.S)
        s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
        s = re.sub(r"/%.*?%/", " ", s, flags=re.S)
    for marker in ("/*", "<!--", "/%"):
        i = s.find(marker)
        if i >= 0:
            s = s[:i]
    j = s.rfind("-->")
    if j >= 0:
        s = s[j + 3:]
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    s = re.sub(r"<<script>>.*?<</script>>", " ", s, flags=re.S)
    s = re.sub(r"<<silently>>.*?<</silently>>", " ", s, flags=re.S)
    # 删整行含宏的
    lines = []
    for ln in s.split("\n"):
        if re.search(r"<<[a-zA-Z]", ln):
            continue
        lines.append(ln)
    s = " ".join(lines)
    s = re.sub(r"<[^>]{1,400}>", " ", s)
    s = re.sub(r"\[\[[^\]]*\]\]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s


# 完整句子：连续 >=5 个英文单词，中间无中文
SENT = re.compile(r"[A-Z][^.!?]{20,300}[.!?]")


per = Counter()
samples = {}
for pname, body in blocks:
    txt = strip_all(body)
    for m in SENT.finditer(txt):
        seg = m.group(0).strip()
        if CJK.search(seg):
            continue
        words = re.findall(r"[A-Za-z']+", seg)
        if len(words) < 5:
            continue
        if not re.search(r"\b(?:the|and|you|is|are|to|of|a|an|in|it|that|this|with|for)\b", seg, re.I):
            continue
        per[pname] += 1
        samples.setdefault(pname, []).append(seg[:130])

print(f"含完整英文句的 passage: {len(per)}   句子总数: {sum(per.values())}\n")
for pname, c in per.most_common(20):
    print(f"  {c:>3}  {pname}")
    for s in samples[pname][:2]:
        print(f"        {s!r}")
