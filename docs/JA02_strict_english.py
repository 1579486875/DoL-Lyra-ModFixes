"""更严格地提取真正的英文剧情句子。

在上一版基础上再加过滤：
  - 含 $ / _变量 / isnot / instanceof 的不要
  - 含 "to $" 这种赋值残渣的不要
  - 首词必须是大写英文单词
  - 必须像自然语言（至少 3 个常见功能词）
"""
import html
import re
from collections import Counter

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
CJK = re.compile(r"[\u4e00-\u9fff]")

SYSTEM = {
    "PassageFooter", "gameStartOnly", "StoryInit", "StoryCaption", "StoryTitle",
    "StoryMenu", "StorySubtitle", "StoryAuthor", "StoryBanner", "StoryData",
    "StoryJavaScript", "StoryStylesheet", "StoryDisplayTitle", "Debug",
}


def strip_all(s):
    s = html.unescape(s)
    for _ in range(3):
        s = re.sub(r"/\*.*?\*/", " ", s, flags=re.S)
        s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
        s = re.sub(r"/%.*?%/", " ", s, flags=re.S)
    for marker in ("/*", "<!--", "/%"):
        i = s.find(marker)
        if 0 <= i < len(s) * 0.6:
            s = s[:i]
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    s = re.sub(r"<<script>>.*?<</script>>", " ", s, flags=re.S)
    s = re.sub(r"<<silently>>.*?<</silently>>", " ", s, flags=re.S)
    lines = [ln for ln in s.split("\n") if not re.search(r"<<[a-zA-Z]", ln)]
    s = " ".join(lines)
    s = re.sub(r"<[^>]{1,400}>", " ", s)
    s = re.sub(r"\[\[[^\]]*\]\]", " ", s)
    return re.sub(r"\s+", " ", s)


SENT = re.compile(r"[A-Z][^.!?]{18,400}[.!?]")

BAD = re.compile(
    r"(?:\$|_\w|\bisnot\b|\binstanceof\b|\btypeof\b|\bnull\b|\bundefined\b|"
    r"\bto\s+\$|\bgt\b|\bgte\b|\blt\b|\blte\b|\bis\s+\$|=>|===|!==)"
)

FUNC = re.compile(r"\b(?:the|a|an|and|or|but|you|your|is|are|was|were|to|of|in|"
                  r"it|that|this|with|for|his|her|he|she|they|them|their|"
                  r"have|has|had|not|no|can|will|would|could|should|from|"
                  r"at|on|as|by|if|when|while|there|here|what|who)\b", re.I)

found = []
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>',
                     raw, re.S):
    pn = html.unescape(m.group(1))
    if pn in SYSTEM or pn.startswith("Widgets "):
        continue
    txt = strip_all(m.group(2))
    for mm in SENT.finditer(txt):
        seg = mm.group(0).strip()
        if CJK.search(seg):
            continue
        if BAD.search(seg):
            continue
        words = re.findall(r"[A-Za-z']+", seg)
        if len(words) < 6:
            continue
        if len(FUNC.findall(seg)) < 3:
            continue
        # 首词必须像正常英文开头
        if not re.match(r"^[A-Z][a-z]", seg):
            continue
        found.append((pn, seg))

print(f"高置信度英文剧情句子: {len(found)}")
print("=" * 94)
per = Counter(p for p, _ in found)
for pn, c in per.most_common(30):
    print(f"  {c:>3}  {pn}")
print("\n" + "=" * 94)
for pn, seg in found:
    print(f"[{pn}] {seg[:200]}")
