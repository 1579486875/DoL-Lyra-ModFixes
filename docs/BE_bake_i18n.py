"""在构建期把 i18n 烤进 index.html。

效果等价于「I18nTweeReplacer 先于 TweeReplacer」：
TweeReplacer 运行时看到的就是中文文本，DoLSims / DomRobin 等
写中文锚点的补丁才能命中（实测多命中 72 条）。

注意：烤入后运行时 I18nTweeReplacer 仍会再跑一遍，但它的 f 是英文、
文本已是中文，绝大多数会失配 —— 不会重复翻译。
"""
import html
import json
import os
import re
import collections

HTML = r"E:\TAML\_dol\work\index_modded6.html"
I18N = r"E:\TAML\_dol\work\i18n_dict.json"

data = open(HTML, "rb").read().decode("utf-8", "replace")

# 按 <tw-passagedata> 切块，逐块应用
PAT = re.compile(r'(<tw-passagedata[^>]*name="([^"]+)"[^>]*>)(.*?)(</tw-passagedata>)', re.S)

d = json.load(open(I18N, "r", encoding="utf-8"))
by_p = collections.defaultdict(list)
for it in d["typeB"]["TypeBInputStoryScript"]:
    if it.get("pN"):
        by_p[it["pN"]].append(it)

total_ok = 0
total_skip = 0
changed_passages = 0


# === widget 名 / setup 键黑名单（由下方 load 时填充）===
_RESERVED = set()


def _build_reserved(data_text):
    """从 index.html 原文里扫出所有不能翻译的标识符。"""
    import html as _h
    g = _h.unescape(data_text)
    for m in re.finditer(r'<<widget\s+"([^"]+)"', g):
        _RESERVED.add(m.group(1))
    # setup 对象的所有键（只收纯 ASCII 的，中文键本来就不该翻）
    for m in re.finditer(r"<<set\s+setup\.(\w+)\s+to", g):
        _RESERVED.add(m.group(1))
    return len(_RESERVED)


n_res = _build_reserved(data)
print(f"  已加载 {n_res} 个保留标识符（widget 名 + setup 键）")


def _is_code_like(text, other=None):
    """判断这条 i18n 条目是否不能参与翻译。

    挡的情况：
      1) 出现 <<widget / <<macro / Macro.add —— 宏名不能变
      2) f 是纯标识符（无空格/标点）且 t 里也含 ASCII 字母
         —— 说明翻译破坏了标识符，如 characteristics -> ch一个racteristics

    不挡的情况：
      - f 是纯标识符但 t 是纯中文，如 Monstergirl -> 怪物女孩（正常 UI 翻译）
      - 含宏的普通文本
    """
    if not text:
        return False
    for kw in ("<<widget", "<<macro", "Macro.add"):
        if kw in text:
            return True
    # widget 名 / setup 键：整条 f 恰好等于它们时不能翻
    if text.strip() in _RESERVED:
        return True
    # 纯标识符：看另一边是否仍是 ASCII（破坏性翻译）
    if other is not None:
        is_ident = bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,60}", text))
        if is_ident and re.search(r"[A-Za-z]", other) and not re.search(r"[\u4e00-\u9fff]", other):
            return True
        # 英文标识符 + 译文里混着 ASCII 标识符（部分保留原文）
        if is_ident and re.search(r"[A-Za-z_]{3,}", other) and re.search(r"[\u4e00-\u9fff]", other):
            return True
    return False


def fix_block(m):
    global total_ok, total_skip, changed_passages
    open_tag, pname, body_esc, close_tag = m.group(1), m.group(2), m.group(3), m.group(4)
    # 关键：passage 名也要反转义（如 "Danube House S&amp;M" -> "Danube House S&M"）
    pname_u = html.unescape(pname)
    lst = by_p.get(pname_u) or by_p.get(pname)
    if not lst:
        return m.group(0)

    body = html.unescape(body_esc)
    orig = body

    for it in sorted(lst, key=lambda x: x.get("pos") or 0, reverse=True):
        f, t = it.get("f"), it.get("t")
        if not f or t is None:
            continue
        # === 安全检查：绝不翻译代码/标识符 ===
        if _is_code_like(f, t) or _is_code_like(t, f):
            total_skip += 1
            continue
        pos = it.get("pos", -1)
        if 0 <= pos <= len(body) and body[pos:pos + len(f)] == f:
            body = body[:pos] + t + body[pos + len(f):]
            total_ok += 1
        elif f in body:
            body = body.replace(f, t, 1)
            total_ok += 1
        else:
            total_skip += 1

    if body == orig:
        return m.group(0)

    changed_passages += 1
    return open_tag + html.escape(body, quote=False) + close_tag


new = PAT.sub(fix_block, data)
open(HTML, "wb").write(new.encode("utf-8"))
print(f"i18n 烤入完成")
print(f"  应用条目: {total_ok}")
print(f"  失配条目: {total_skip}")
print(f"  改动 passage: {changed_passages}")
print(f"  文件大小: {os.path.getsize(HTML):,} 字节")
