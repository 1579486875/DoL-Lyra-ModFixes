"""全量补齐（分块版）：按 passage 处理，避免 10 万条 × 100MB 的全局搜索。

核心思路：
  1. 把 index 按 <tw-passagedata> 切成 16087 块
  2. 把 i18n 条目按 pN 分到对应的块
  3. 每块内只做本块条目的全量替换（不看 pos）
  4. 对 pN 对不上的条目，收集起来做一次全局兜底（限长句）

安全阀：f 长度 >= 6、无代码字符、含空格或标点、不是标识符。
"""
import html as H
import json
import os
import re
import sys
from collections import Counter, defaultdict

HTML = r"E:\TAML\_dol\work\index_modded6.html"
I18N = r"E:\TAML\_dol\work\i18n_dict.json"


def is_safe(f, reserved):
    if not f or len(f) < 6:
        return False
    if re.search(r"[<>$`{}\\]", f):
        return False
    if not re.search(r"[\s,.!?;:'\"\-]", f):
        return False
    if f.strip() in reserved:
        return False
    return True


def main():
    print("加载 i18n...")
    d = json.load(open(I18N, "r", encoding="utf-8"))
    items = d["typeB"]["TypeBInputStoryScript"]
    by_p = defaultdict(list)
    for it in items:
        pn = it.get("pN")
        if pn:
            by_p[pn].append(it)
    print(f"  条目 {len(items)}，passage {len(by_p)}")

    print("加载 index...")
    raw = open(HTML, "rb").read().decode("utf-8", "replace")
    size0 = len(raw)

    # 建保留标识符
    g_all = H.unescape(raw)
    reserved = set(re.findall(r'<<widget\s+"([^"]+)"', g_all))
    reserved |= set(re.findall(r"<<set\s+setup\.(\w+)\s+to", g_all))
    print(f"  保留标识符 {len(reserved)}")

    # 按 passage 切块
    PAT = re.compile(r'(<tw-passagedata[^>]*name="([^"]+)"[^>]*>)(.*?)(</tw-passagedata>)', re.S)

    stats = Counter()
    unmatched = []   # pN 对不上的条目

    def fix_block(m):
        open_tag, pname_esc, body_esc, close_tag = m.group(1), m.group(2), m.group(3), m.group(4)
        pname = H.unescape(pname_esc)
        lst = by_p.get(pname)
        if not lst:
            return m.group(0)

        body = H.unescape(body_esc)
        orig = body
        local = 0

        # 按 f 长度降序，避免短串先破坏长串
        for it in sorted(lst, key=lambda x: -len(x.get("f") or "")):
            f, t = it.get("f"), it.get("t")
            if not f or t is None or f == t:
                stats["空或相同"] += 1
                continue
            if not is_safe(f, reserved):
                stats["不安全"] += 1
                continue
            if f not in body:
                stats["本块已不存在"] += 1
                continue
            n = body.count(f)
            body = body.replace(f, t)
            local += n

        if body == orig:
            return m.group(0)
        stats["替换次数"] += local
        stats["改动 passage"] += 1
        return open_tag + H.escape(body, quote=False) + close_tag

    print("\n分块处理...")
    new_raw = PAT.sub(fix_block, raw)

    print(f"\n=== 分块结果 ===")
    for k, v in stats.most_common():
        print(f"  {k}: {v}")
    print(f"  index: {size0:,} -> {len(new_raw):,} ({len(new_raw)-size0:+,})")

    # 全局兜底：把没 pN 或 pN 对不上的长句做一次替换
    print("\n全局兜底（长句 >= 20 字符，最多 3000 条）...")
    handled = set()
    for pn, lst in by_p.items():
        for it in lst:
            handled.add(id(it))

    global_cands = []
    for it in items:
        if id(it) in handled:
            continue
        f, t = it.get("f"), it.get("t")
        if not f or t is None or f == t:
            continue
        if not is_safe(f, reserved):
            continue
        if len(f) < 20:
            continue
        global_cands.append(it)
    global_cands.sort(key=lambda x: -len(x["f"]))
    global_cands = global_cands[:3000]
    print(f"  候选 {len(global_cands)} 条")

    g_new = 0
    for it in global_cands:
        f, t = it["f"], it["t"]
        a = H.escape(f, quote=False)
        if a in new_raw:
            n = new_raw.count(a)
            new_raw = new_raw.replace(a, t if False else H.escape(t, quote=False))
            g_new += n
    print(f"  全局补充替换 {g_new} 处")

    open(HTML, "wb").write(new_raw.encode("utf-8"))
    print(f"\n写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")

    # 校验
    g = H.unescape(new_raw)
    print(f"\n中文字符: {len(re.findall(r'[\u4e00-\u9fff]', g)):,}")
    names = re.findall(r'<<widget\s+"([^"]+)"', g)
    bad = [n for n in names if re.search(r"[^\x00-\x7f]", n)]
    print(f"widget 名含非 ASCII: {len(bad)}  {bad[:5] if bad else '✅'}")
    nested = sum(1 for m in re.finditer(r'<<widget\s+"([^"]+)"\s*>>(.*?)<</widget>>', g, re.S)
                 if "<<widget" in m.group(2))
    print(f"widget 嵌套: {nested}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
