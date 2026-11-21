"""BE2（第12轮重写 BE_bake_i18n）：构建期把 ModI18N 官方 passage 译文烘焙进 index。

旧版 BE_bake 的 bug（第12轮运行时实测）：
  只在 pos 处做精确比较，失败就退回 body.replace(f, t, 1)「替换第一处出现」。
  而官方 i18n 的 pos 有 31121 条相对 vanilla 偏了 -1/-2（ModI18N 自己按 ±2 容错），
  这些条目全部走了「替换第一处」—— 原文在 passage 里重复出现时就替换到了别的位置：
    · 正确位置留下英文（运行时英文残留，实测基线 166 段官方有译文却显示英文）；
    · 错误位置被替换，把同 passage 里另一条（更长的）条目的原文打断 → 那条也失配。
  例：Avery School Pickup Accept 的「Robin watches you climb into the car…」在两个分支各出现一次，
      第二条把第一分支里的半句换掉，第一分支整句 "You decide it's best not to push things. …" 失配，留下半英半中。

新算法 = ModI18N 1.0.1a 运行时的 replacePassageContentWithHintIndex（tryReplaceStringFuzzyWithHintIndexComp）：
  同一 passage 的条目按 pos 升序；每条先在 pos, pos-1, pos-2, pos+1, pos+2 精确比较，
  再在 [pos-10, pos+len+30] 窗口内找；命中位置必须 ≥ 上一条的结束位置（不重叠）。
  与运行时不同之处：某条失配时**只跳过这一条**（运行时会放弃整个 passage）。
  不再使用「替换第一处出现」的兜底。
安全检查（_is_code_like：widget 名 / setup 键 / 标识符不翻译）与旧版一致。
"""
import collections
import html
import os
import re
import sys

HTML = os.environ.get("DOL_HTML") or r"E:\TAML\_dol\work\index_modded6.html"
I18N = r"E:\TAML\_dol\work\i18n_dict.json"


def _load_i18n(path):
    import json
    import pickle
    cache = path + ".pkl"
    try:
        if os.path.exists(cache) and os.path.getmtime(cache) > os.path.getmtime(path):
            with open(cache, "rb") as f:
                return pickle.load(f)
    except Exception:
        pass
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    try:
        with open(cache, "wb") as f:
            pickle.dump(d, f, protocol=4)
    except Exception:
        pass
    return d


data = open(HTML, "rb").read().decode("utf-8", "replace")
if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[BE2] index 形态异常")
    sys.exit(1)

PAT = re.compile(r'(<tw-passagedata[^>]*name="([^"]+)"[^>]*>)(.*?)(</tw-passagedata>)', re.S)
d = _load_i18n(I18N)
by_p = collections.defaultdict(list)
for it in d["typeB"]["TypeBInputStoryScript"]:
    if it.get("pN"):
        by_p[it["pN"]].append(it)

_RESERVED = set()


def _build_reserved(data_text):
    g = html.unescape(data_text)
    for m in re.finditer(r'<<widget\s+"([^"]+)"', g):
        _RESERVED.add(m.group(1))
    for m in re.finditer(r"<<set\s+setup\.(\w+)\s+to", g):
        _RESERVED.add(m.group(1))
    return len(_RESERVED)


def _is_code_like(text, other=None):
    if not text:
        return False
    for kw in ("<<widget", "<<macro", "Macro.add"):
        if kw in text:
            return True
    if text.strip() in _RESERVED:
        return True
    if other is not None:
        is_ident = bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,60}", text))
        if is_ident and re.search(r"[A-Za-z]", other) and not re.search(r"[\u4e00-\u9fff]", other):
            return True
        if is_ident and re.search(r"[A-Za-z_]{3,}", other) and re.search(r"[\u4e00-\u9fff]", other):
            return True
    return False


n_res = _build_reserved(data)
print(f"  已加载 {n_res} 个保留标识符（widget 名 + setup 键）")

stat = collections.Counter()
fail_by_p = collections.Counter()
changed_passages = 0


def locate(s, f, pos, last):
    for off in (pos, pos - 1, pos - 2, pos + 1, pos + 2):
        if off >= last and off >= 0 and off + len(f) <= len(s) and s.startswith(f, off):
            return off
    st = max(0, pos - 10, last)
    en = min(len(s), pos + len(f) + 30)
    if en - st >= len(f):
        k = s.find(f, st, en)
        if k >= 0:
            return k
    return None


def fix_block(m):
    global changed_passages
    open_tag, pname, body_esc, close_tag = m.group(1), m.group(2), m.group(3), m.group(4)
    pname_u = html.unescape(pname)
    lst = by_p.get(pname_u) or by_p.get(pname)
    if not lst:
        return m.group(0)
    s = html.unescape(body_esc)
    out = []
    last = 0
    for it in sorted(lst, key=lambda x: x.get("pos") or 0):
        f, t, pos = it.get("f"), it.get("t"), it.get("pos") or 0
        if not f or t is None:
            stat["无效"] += 1
            continue
        if _is_code_like(f, t) or _is_code_like(t, f):
            stat["代码类跳过"] += 1
            continue
        k = locate(s, f, pos, last)
        if k is None:
            stat["失配"] += 1
            fail_by_p[pname_u] += 1
            continue
        out.append(s[last:k])
        out.append(t)
        last = k + len(f)
        stat["应用"] += 1
    out.append(s[last:])
    new = "".join(out)
    if new == s:
        return m.group(0)
    changed_passages += 1
    return open_tag + html.escape(new, quote=False) + close_tag


new = PAT.sub(fix_block, data)
n_after = len(re.findall(r'<tw-passagedata[^>]*name="', new))
if n_after != len(re.findall(r'<tw-passagedata[^>]*name="', data)):
    print("[BE2] FAIL passage 数变化")
    sys.exit(1)
open(HTML, "wb").write(new.encode("utf-8"))
print("[BE2] i18n 烘焙：应用 %d / 失配 %d / 代码类跳过 %d / 无效 %d   改动 passage %d" % (
    stat["应用"], stat["失配"], stat["代码类跳过"], stat["无效"], changed_passages))
if fail_by_p:
    print("  失配最多的 passage:", fail_by_p.most_common(10))
# 失配率异常（>1%）说明 index 不是 vanilla 原文，拒绝继续
tot = stat["应用"] + stat["失配"]
sys.exit(1 if tot and stat["失配"] / tot > 0.01 else 0)
