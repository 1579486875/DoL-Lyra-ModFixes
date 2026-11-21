"""AF01（第12轮-2）：修 Wraith'sReflection「银制海螺对话」的多行字符串语法错误（幂等）。

现象：<<ChatWR>> widget 里 <<set _chat.push("……\n<br><br>\n……")>> 的双引号字符串跨了行。
      <<set>> 的参数原样交给 eval，JS 双引号字符串不允许裸换行 → SyntaxError，
      _chat 一直是空数组 → 「对海螺说话」(Silver Conch Talk) 没有任何对话内容。
修法（① 保意图）：只在这几处 <<set _chat.push(...)>> 的字符串字面量内部，把「换行+缩进」
      折叠成一个空格。文本一字不改；作者用来分段的 <br><br> 原样保留
      （若改成反引号模板串，换行会被 SugarCube 渲染成额外的 <br>，与作者排版不符）。
判据：T03_sc_compile_all.js --twee-dir 扫模组 twee，编译失败 = 0。
"""
import os
import re
import sys

sys.path.insert(0, r"E:\TAML\_dol\work")
import modzip_lib as MZ
import scan_lib as SL

HTML = os.environ.get("DOL_HTML") or r"E:\TAML\_dol\work\index_modded6.html"
MOD = "Wraith'sReflection"
FILE = "game/WraithsReflectionTwee/SilverConchTalk.twee"
MARK = "<!-- [AF01] multiline-string-fixed -->"

data = open(HTML, "rb").read().decode("utf-8", "replace")
if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[AF01] index 形态异常")
    sys.exit(1)

cur = MZ.read_mod_file(data, MOD, FILE)
if cur is None:
    print("[AF01] FAIL 找不到 %s / %s" % (MOD, FILE))
    sys.exit(1)
if MARK.encode("utf-8") in cur:
    print("[AF01] 已存在，跳过")
    sys.exit(0)

STR = re.compile(r'"(?:[^"\\]|\\.)*"', re.S)
stats = {"macro": 0, "str": 0}


def fix_twee(txt):
    out = []
    pos = 0
    for m in re.finditer(r"<<set _chat\.push\(", txt):
        if m.start() < pos:
            continue
        e = SL.args_end(txt, m.start() + 5)
        if e < 0:
            continue
        seg = txt[m.start():e]
        n0 = stats["str"]

        def coll(sm):
            s = sm.group(0)
            if "\n" not in s:
                return s
            stats["str"] += 1
            return re.sub(r"[ \t]*\n[ \t]*", " ", s)
        seg2 = STR.sub(coll, seg)
        if stats["str"] > n0:
            stats["macro"] += 1
        out.append(txt[pos:m.start()])
        out.append(seg2)
        pos = e
    out.append(txt[pos:])
    return "".join(out)


def fn(name, d):
    if name != FILE:
        return None
    txt = d.decode("utf-8")
    nl = "\r\n" if "\r\n" in txt else "\n"
    t = txt.replace("\r\n", "\n")
    t2 = fix_twee(t)
    if t2 == t:
        return None
    # 在 widget passage 头之后加标记注释（<!-- --> 不显示）
    t2 = t2.replace(":: Widget Silver Conch Talk [widget]\n", ":: Widget Silver Conch Talk [widget]\n" + MARK + "\n", 1)
    return t2.replace("\n", nl).encode("utf-8")


data2, changed = MZ.patch_mod(data, MOD, fn)
if not changed:
    print("[AF01] FAIL 没有可修的内容")
    sys.exit(1)

# 校验：重新读出该文件，编译检查用 scan_lib 的宏边界 + 「字符串内无裸换行」
chk = MZ.read_mod_file(data2, MOD, FILE).decode("utf-8")
bad = 0
for mm in re.finditer(r"<<set _chat\.push\(", chk):
    e = SL.args_end(chk, mm.start() + 5)
    for sm in STR.finditer(chk[mm.start():e]):
        if "\n" in sm.group(0):
            bad += 1
if bad or MARK not in chk:
    print("[AF01] FAIL 校验未过 bad=%d mark=%s" % (bad, MARK in chk))
    sys.exit(1)
open(HTML, "wb").write(data2.encode("utf-8"))
print("[AF01] 修 %d 个 <<set _chat.push>> / %d 个跨行字符串  文件=%s  OK" % (stats["macro"], stats["str"], changed))
