"""AU01：运行时英文残留扫描（以运行时导出为准，对照 vanilla 同名 passage）。

只统计「玩家可见文本」：去掉注释、<<script>>、宏标签（保留宏外文字）、HTML 标签后，
找连续 ≥4 个英文单词的片段；该片段在 vanilla 同名 passage 里也逐字存在 → 判定为「未翻译的原文」。
用法: python AU01_runtime_english.py <runtime.jsonl> [对照 runtime.jsonl]
"""
import json
import re
import sys
from collections import Counter

sys.path.insert(0, r"E:\TAML\_dol\work")
import scan_lib as L

V = {n: b for n, t, b in L.passages(open(r"E:\TAML\_dol\work\index.html", "rb").read().decode("utf-8", "replace"))}
SENT = re.compile(r"[A-Za-z][A-Za-z'’,\-]*(?:[ \t]+[A-Za-z][A-Za-z'’,\-]*){3,}[.!?…]?")


def visible(body):
    s = L.prep(body)
    out = list(s)
    pos = 0
    while True:
        i = s.find("<<", pos)
        if i < 0:
            break
        if s.startswith("<</", i):
            j = s.find(">>", i)
            if j < 0:
                break
            for k in range(i, j + 2):
                out[k] = " "
            pos = j + 2
            continue
        m = L.MACRO_RE.match(s, i)
        if not m:
            pos = i + 2
            continue
        e = L.args_end(s, m.end())
        if e < 0:
            pos = i + 2
            continue
        for k in range(i, e + 2):
            if out[k] != "\n":
                out[k] = " "
        pos = e + 2
    s = "".join(out)
    s = re.sub(r"<[^<>]*>", lambda m: " " * len(m.group(0)), s)
    s = re.sub(r"\[\[[^\]]*\]\]", " ", s)
    return s


def scan(path):
    out = {}
    for line in open(path, encoding="utf-8"):
        t, tg, body = json.loads(line)
        if "script" in tg.split() or t not in V:
            continue
        vb = V[t]
        hits = []
        for m in SENT.finditer(visible(body)):
            frag = m.group(0).strip()
            if len(frag) < 18 or frag not in vb or frag in V:
                continue
            hits.append(frag)
        if hits:
            out[t] = hits
    return out


cur = scan(sys.argv[1])
n = sum(len(v) for v in cur.values())
print("运行时英文残留（vanilla 原文逐字未改）：%d 个 passage / %d 段" % (len(cur), n))
if len(sys.argv) > 2:
    base = scan(sys.argv[2])
    nb = sum(len(v) for v in base.values())
    new = {k: [x for x in v if x not in base.get(k, [])] for k, v in cur.items()}
    new = {k: v for k, v in new.items() if v}
    print("对照：%d 个 passage / %d 段；当前新增 %d 段（%d 个 passage）" % (len(base), nb, sum(len(v) for v in new.values()), len(new)))
    for k, v in list(new.items())[:40]:
        print("  +[%s] %s" % (k, v[:3]))
c = Counter({k: len(v) for k, v in cur.items()})
print("残留最多的 passage：")
for k, v in c.most_common(40):
    print("  %3d  %s   例: %s" % (v, k, cur[k][0][:90]))
json.dump(cur, open(r"E:\TAML\_dol\work\_au01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
