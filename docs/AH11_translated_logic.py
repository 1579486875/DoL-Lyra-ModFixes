"""AH11：找出所有「依赖被翻译的显示值做逻辑判断」的位置（社区 issue #583 同类问题）。
做法：收集 vanilla 里 <<set X to "英文">> 被汉化改成 <<set X to "中文">> 的变量（X 为 $/_ 变量），
再看当前包中这些变量是否出现在比较表达式里（is / isnot / === / includes / case）与英文字面量比较。
"""
import re
import sys
from collections import defaultdict

sys.path.insert(0, r"E:\TAML\_dol\work")
import scan_lib as L

CJK = re.compile(r"[\u4e00-\u9fff]")
V = {n: b for n, t, b in L.passages(open(r"E:\TAML\_dol\work\index.html", "rb").read().decode("utf-8", "replace"))}
C = {n: b for n, t, b in L.passages(open(r"E:\TAML\_dol\work\_cur_index.html", "rb").read().decode("utf-8", "replace"))}
SETRE = re.compile(r"^\s*([$_][\w.\[\]\"']+)\s+to\s+([\"'`])(.*?)\2\s*$", re.S)


def sets(body):
    out = []
    for mac, args, st in L.iter_macros(body):
        if mac == "set":
            m = SETRE.match(args)
            if m:
                out.append((m.group(1), m.group(3)))
    return out


changed = defaultdict(set)   # 变量 -> {(英文, 中文)}
for n, cb in C.items():
    if n not in V:
        continue
    sv, sc = sets(V[n]), sets(cb)
    if len(sv) != len(sc):
        continue
    for (va, vv), (ca, cv) in zip(sv, sc):
        if va == ca and vv != cv and not CJK.search(vv) and CJK.search(cv) and re.fullmatch(r"[A-Za-z][A-Za-z \-']{0,30}", vv):
            changed[va].add((vv, cv))

print("被汉化改了赋值字面量的变量: %d 个" % len(changed))
# 当前包里：这些变量（或被它们赋值的变量）与英文字面量比较
hits = []
for n, cb in C.items():
    for mac, args, st in L.iter_macros(cb):
        if mac not in ("if", "elseif", "switch", "case", "set", "print", "=", "run"):
            continue
        for var, pairs in changed.items():
            if var not in args:
                continue
            ens = {e for e, c in pairs}
            for e in ens:
                if re.search(re.escape(var) + r"\s*(?:is|isnot|===|!==|==|!=|eq|neq)\s*[\"'`]" + re.escape(e) + r"[\"'`]", args) or \
                   re.search(r"[\"'`]" + re.escape(e) + r"[\"'`]\s*(?:is|isnot|===|!==|==|!=)\s*" + re.escape(var), args):
                    hits.append((n, mac, var, e, args.strip()[:160]))
print("当前包里拿英文值比较、但赋值已变中文的: %d 处" % len(hits))
for h in hits:
    print("  ", h)
# 另：被赋中文的变量又被赋给别的变量（如 $remyEscapeSteed to _text_output）
print("\n二次传递（X to <被汉化的变量>）:")
for n, cb in C.items():
    for mac, args, st in L.iter_macros(cb):
        if mac == "set":
            m = re.match(r"^\s*([$_][\w.]+)\s+to\s+([$_][\w.]+)\s*$", args)
            if m and m.group(2) in changed:
                print("   [%s] <<set %s>>  ← %s 的值已被汉化 %s" % (n, args.strip(), m.group(2), sorted(changed[m.group(2)])[:4]))
