"""第 22 轮：改进英文检测器 —— 彻底剥离注释与代码，只留玩家可见文本。

改进点：
1. /* ... */ 与 <!-- ... --> 允许不配对（游戏源码里存在）
2. 孤立 --> 之前的内容视为注释
3. 剔除 <<exit>> / <<set>> 等宏的参数里的 JS
4. 只统计「被中文包围」或「位于纯文本区」的英文句子
"""
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
    # 1) 成对注释
    for _ in range(3):
        s = re.sub(r"/\*.*?\*/", " ", s, flags=re.S)
        s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
        s = re.sub(r"/%.*?%/", " ", s, flags=re.S)
    # 2) 不配对的：孤立 /* 或 <!-- 之后全删
    for marker in ("/*", "<!--", "/%"):
        i = s.find(marker)
        if i >= 0:
            s = s[:i]
    # 3) 孤立 --> 之前全删
    j = s.rfind("-->")
    if j >= 0:
        s = s[j + 3:]
    # 4) 脚本 / 样式
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    s = re.sub(r"<<script>>.*?<</script>>", " ", s, flags=re.S)
    s = re.sub(r"<<silently>>.*?<</silently>>", " ", s, flags=re.S)
    # 5) 宏
    s = re.sub(r"<<[a-zA-Z][^>]*>>", " ", s)
    # 6) HTML 标签
    s = re.sub(r"<[^>]{1,400}>", " ", s)
    # 7) wiki 链接
    s = re.sub(r"\[\[[^\]]*\]\]", " ", s)
    # 8) JS 片段（含 => { } ; 的长串）
    s = re.sub(r"\{[^{}]{0,400}\}", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s


SENT = re.compile(
    r"\b(?:[A-Z][a-z']{1,15}|[a-z']{2,15})"
    r"(?:\s+(?:[A-Za-z][a-z']{0,15}|[,.!?;:'\"-])){3,60}",
)

per = Counter()
samples = {}
for pname, body in blocks:
    txt = strip_all(body)
    for m in SENT.finditer(txt):
        seg = m.group(0).strip()
        if not re.search(r"\b(?:the|and|you|is|are|to|of|a|an|in|it|that|this|with|for|was|were)\b", seg, re.I):
            continue
        if CJK.search(seg) or len(seg) < 15:
            continue
        # 排除明显的 JS 关键字
        if re.search(r"\b(?:function|return|var|let|const|typeof|undefined|null|true|false|else|for|while|switch|case|break|default)\b", seg):
            continue
        per[pname] += 1
        samples.setdefault(pname, []).append(seg[:110])

print(f"含英文句的 passage: {len(per)}   句子总数: {sum(per.values())}\n")
for pname, c in per.most_common(15):
    print(f"  {c:>3}  {pname}")
    for s in samples[pname][:2]:
        print(f"        {s!r}")
