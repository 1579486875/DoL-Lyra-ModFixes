"""scan_lib：审计用的公共函数（第12轮建立）。

所有判据都基于「SugarCube 宏参数的真实边界」，而不是 [^<>]{0,800} 这类会漏判的正则
（§5.12：[^<>] 匹配不到含 < 的内容 → 报 0 处；长度上限会漏掉长 <<set>>）。
"""
import html as H
import re

CJK = re.compile(r"[\u4e00-\u9fff]")


def passages(raw):
    """raw（转义形态）→ [(name, tags, body_unescaped)]"""
    out = []
    for m in re.finditer(r'<tw-passagedata\s+([^>]*)>(.*?)</tw-passagedata>', raw, re.S):
        nm = re.search(r'name="([^"]*)"', m.group(1))
        tg = re.search(r'tags="([^"]*)"', m.group(1))
        if not nm:
            continue
        out.append((H.unescape(nm.group(1)), tg.group(1) if tg else "", H.unescape(m.group(2))))
    return out


def _blank(s, pat, flags=0):
    return re.sub(pat, lambda m: re.sub(r"[^\n]", " ", m.group(0)), s, flags=flags)


def prep(body):
    """把不参与宏解析的区域（注释 / nowiki / <<script>> 块）抹成等长空白。"""
    s = body
    s = _blank(s, r"/\*.*?\*/", re.S)
    s = _blank(s, r"/%.*?%/", re.S)
    s = _blank(s, r"<!--.*?-->", re.S)
    s = _blank(s, r'""".*?"""', re.S)
    s = _blank(s, r"<nowiki>.*?</nowiki>", re.S | re.I)
    s = _blank(s, r"\{\{\{.*?\}\}\}", re.S)
    s = _blank(s, r"<<script>>.*?<</script>>", re.S)
    return s


def args_end(s, i):
    """从宏名之后的位置 i 开始，找配对的 >>（跳过引号 / 反引号 / [[ ]]）。"""
    q = None
    sq = 0
    n = len(s)
    while i < n:
        c = s[i]
        if q:
            if c == "\\":
                i += 2
                continue
            if c == q:
                q = None
            i += 1
            continue
        if c in "\"'`":
            q = c
        elif c == "[" and s.startswith("[[", i):
            sq += 1
            i += 2
            continue
        elif c == "]" and sq and s.startswith("]]", i):
            sq -= 1
            i += 2
            continue
        elif c == ">" and sq == 0 and s.startswith(">>", i):
            return i
        i += 1
    return -1


MACRO_RE = re.compile(r"<<([A-Za-z][\w-]*|=|-)(?=[\s>])")


def iter_macros(body):
    """逐个产出 (宏名, 参数原文, 起始下标)。宏参数会吞掉其内部字符串里的 <<...>>（与引擎一致）。"""
    s = prep(body)
    pos = 0
    while True:
        m = MACRO_RE.search(s, pos)
        if not m:
            return
        a0 = m.end()
        e = args_end(s, a0)
        if e < 0:
            pos = a0
            continue
        yield m.group(1), body[a0:e], m.start()
        pos = e + 2


_STR_RE = re.compile(r'"(?:[^"\\]|\\.)*"|' + r"'(?:[^'\\]|\\.)*'|" + r"`(?:[^`\\]|\\.)*`", re.S)


def mask_strings(s):
    """把字符串 / 模板串抹成等长空白，只留代码。

    必须单趟、按出现顺序处理三种引号：分三趟先抹双引号会把 `\\"x\\"` 这类模板串里的
    双引号当成字符串起点，导致后续全部错位（第12轮实测误报 2 处）。
    """
    return _STR_RE.sub(lambda m: " " * len(m.group(0)), s)


CODE_MACROS = {"if", "elseif", "set", "run", "switch", "for", "print", "=", "-"}

# ---- 宏结构（照抄引擎 Wikifier.Parser "macro" 的 lookahead 正则）----
_MN = r"[A-Za-z][\w-]*|[=-]"
TAG_RE = re.compile(r"<<(/?(?:" + _MN + r"))(?:\s*)((?:(?:/\*[^*]*\*+(?:[^/*][^*]*\*+)*/)|(?://.*\n)|(?:`(?:\\.|[^`\\])*`)"
                    r"|(?:\"(?:\\.|[^\"\\])*\")|(?:'(?:\\.|[^'\\])*')|(?:\[(?:[<>]?[Ii][Mm][Gg])?\[[^\r\n]*?\]\]+)|[^>]|(?:>(?!>)))*)>>", re.M)
CHILD = {"elseif": "if", "else": "if", "case": "switch", "default": "switch"}


def macro_tags(body):
    s = prep(body)
    out = []
    pos = 0
    while True:
        i = s.find("<<", pos)
        if i < 0:
            break
        m = TAG_RE.match(s, i)
        if not m:
            pos = i + 2
            continue
        out.append((m.group(1), i))
        pos = m.end()
    return out


def struct_errors(tl, cont):
    """引擎语义：容器宏向后找同名闭合（同名计深度）；子标签必须落在父容器体内；
    第12轮补：无主的闭合标签（<</for>> 前没有 <<for>>）与不存在的闭合宏（<</div>> 这类）也报错。"""
    errs = []
    n = len(tl)
    owned = set()
    closed = set()
    for k, (nm, pos) in enumerate(tl):
        if nm in cont:
            depth = 1
            j = k + 1
            while j < n:
                t = tl[j][0]
                if t == nm:
                    depth += 1
                elif t == "/" + nm or t == "end" + nm:
                    depth -= 1
                    if depth == 0:
                        closed.add(j)
                        break
                elif depth == 1 and CHILD.get(t) == nm:
                    owned.add(j)
                j += 1
            if j >= n:
                errs.append("cannot find a closing tag for macro <<%s>> @%d" % (nm, pos))
    for k, (nm, pos) in enumerate(tl):
        if nm in CHILD and k not in owned:
            errs.append("child tag <<%s>> outside @%d" % (nm, pos))
        elif nm.startswith("/") and k not in closed:
            if nm[1:] in cont:
                errs.append("orphan closing tag <<%s>> @%d" % (nm, pos))
            else:
                errs.append("macro <<%s>> does not exist @%d" % (nm, pos))
    return errs


def struct_regressions(van_raw, cur_raw):
    """当前包比 vanilla 多出引擎级结构错误的 passage → {name: [错误]}（对照 vanilla，不是对照汉化基线）。"""
    gv = van_raw.replace("&lt;", "<").replace("&gt;", ">")
    gc = cur_raw.replace("&lt;", "<").replace("&gt;", ">")
    cont = set(re.findall(r"<</([A-Za-z][\w-]*)>>", gv))
    # 模组新增的容器宏（如 maplebirch 的 <<lanLink>>…<</lanLink>>）：当前包里同时有开、闭标签就算容器
    _cl = set(re.findall(r"<</([A-Za-z][\w-]*)>>", gc))
    _op = set(re.findall(r"<<([A-Za-z][\w-]*)[\s>]", gc))
    cont |= (_cl & _op)
    cont -= {"div", "span", "svg"}
    keep = lambda nm: nm.lstrip("/") in cont or nm in CHILD or nm.startswith("/")
    V = {n: b for n, t, b in passages(van_raw)}
    bad = {}
    for n, t, cb in passages(cur_raw):
        if n not in V:
            continue
        tc = [x for x in macro_tags(cb) if keep(x[0])]
        tv = [x for x in macro_tags(V[n]) if keep(x[0])]
        if [x[0] for x in tc] == [x[0] for x in tv]:
            continue
        ec, ev = struct_errors(tc, cont), struct_errors(tv, cont)
        if len(ec) > len(ev):
            bad[n] = ec[:6]
    return bad


def cjk_in_code(raw):
    """宏表达式（挖掉字符串后）里出现中文 = 标识符/属性名/关键字被翻译。返回 [(passage, 宏, 片段)]"""
    hits = []
    for name, tags, body in passages(raw):
        if re.search(r"\b(script|stylesheet)\b", tags):
            continue
        for mac, args, st in iter_macros(body):
            if mac not in CODE_MACROS:
                continue
            code = mask_strings(args)
            mm = CJK.search(code)
            if mm:
                hits.append((name, mac, args[max(0, mm.start() - 40):mm.start() + 40].replace("\n", " ")))
    return hits
