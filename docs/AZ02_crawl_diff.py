"""AZ02（第14轮）：passage 遍历结果对比（整合包 vs vanilla）。

两边都从「新档 Start2 之后」的同一状态出发，所以「缺状态」类红字两边大体相同；
整合包独有、或比 vanilla 多出的「语法/结构/未定义」类红字才是确定的回归。
用法: python AZ02_crawl_diff.py [_crawl_mod.jsonl] [_crawl_van.jsonl]
"""
import json
import re
import sys
from collections import Counter, defaultdict

mod = sys.argv[1] if len(sys.argv) > 1 else r"E:\TAML\_dol\work\_crawl_mod.jsonl"
van = sys.argv[2] if len(sys.argv) > 2 else r"E:\TAML\_dol\work\_crawl_van.jsonl"
HARD = re.compile(r"SyntaxError|does not exist|cannot find a closing tag|child tag|is not defined|is not a function|"
                  r"Unexpected token|Invalid or unexpected|missing \) after|Malformed|ReferenceError")


def kind(msg):
    m = re.search(r"(macro <<[^>]+>> does not exist|cannot find a closing tag for macro <<\w+>>|child tag <<[^>]+>> was found outside[^;)]*|"
                  r"(?:Syntax|Reference|Type|Range)Error: [^;)\n]{0,90}|Undefined NPC in \w+|is not a function|is not defined)", msg)
    k = m.group(1) if m else msg[:80]
    k = re.sub(r"'[^']{0,40}'", "'…'", k)
    k = re.sub(r"\d+", "#", k)
    return k


def load(p):
    out = {}
    for line in open(p, encoding="utf-8"):
        n, c, msgs, ms, end = json.loads(line)
        out[n] = (c, [kind(x) for x in msgs], msgs)
    return out


M, V = load(mod), load(van)
both = [n for n in M if n in V]
print("遍历 passage：整合包 %d / vanilla %d / 共同 %d" % (len(M), len(V), len(both)))
print("有红字：整合包 %d / vanilla %d" % (sum(1 for n in both if M[n][0] > 0), sum(1 for n in both if V[n][0] > 0)))
print("脚本异常（-1/-9）：整合包 %d / vanilla %d" % (sum(1 for n in both if M[n][0] < 0), sum(1 for n in both if V[n][0] < 0)))
only, worse, hard_new = [], [], []
for n in both:
    mc, mk, mm = M[n]
    vc, vk, vm = V[n]
    if mc > 0 and vc == 0:
        only.append(n)
    elif mc > vc >= 0:
        worse.append(n)
    newk = [k for k in mk if k not in vk]
    if any(HARD.search(x) for x in newk):
        hard_new.append((n, [k for k in newk if HARD.search(k)], mm[:1]))
print("整合包独有红字 %d 个 passage；红字比 vanilla 多 %d 个" % (len(only), len(worse)))
agg = Counter()
for n in only + worse:
    for k in M[n][1]:
        if k not in V[n][1]:
            agg[k] += 1
print("\n== 整合包新增的错误类型（按 passage 计）top 40")
for k, c in agg.most_common(40):
    print("  %4d  %s" % (c, k))
print("\n== 语法/结构/未定义 类新增（确定的回归）%d 个 passage" % len(hard_new))
for n, ks, mm in hard_new[:80]:
    print("  [%s] %s\n        %s" % (n, ks[:2], (mm[0] if mm else "")[:260].replace("\n", " ")))
json.dump({"only": only, "worse": worse, "hard_new": hard_new}, open(r"E:\TAML\_dol\work\_az02.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
