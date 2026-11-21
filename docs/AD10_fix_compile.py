"""AD10（第12轮-1）：修复「引擎 parse 后无法编译」的宏表达式（幂等）。

判据来自 T03_sc_compile_all.js（用游戏引擎自带的 Scripting.parse + new Function 编译）。
全部是 ① 保意图修复：只修引号/反引号/逗号/括号/全角标点，文本内容不动。

来源分三类：
  [译] 翻译破坏（i18n 把反引号换成了双引号、句号换成全角、括号挪位、属性名被翻译）
  [原] 原版就有的语法错误（vanilla 同样报错；修法与作者意图一致）
"""
import html as H
import os
import re
import sys

HTML = os.environ.get("DOL_HTML") or r"E:\TAML\_dol\work\index_modded6.html"
VANILLA = r"E:\TAML\_dol\work\index.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[AD10] index 形态异常")
    sys.exit(1)

MARK = "[AD10]"
if MARK in H.unescape(data):
    print("[AD10] 已存在，跳过")
    sys.exit(0)

BT = chr(96)


def passage_span(raw, name):
    m = re.search(r'<tw-passagedata\s+[^>]*name="' + re.escape(name) + r'"[^>]*>', raw)
    if not m:
        return None
    e = raw.find("</tw-passagedata>", m.end())
    return m.end(), e


# (passage, old, new, 期望命中次数, 类别)
FIXES = [
    # ---- Avery ----
    ("Widgets speech-Avery",
     '小<<= either("<<bitch>>","<<bastard>>","<<cunt>>")>>？"',
     "小<<= either('<<bitch>>','<<bastard>>','<<cunt>>')>>？\"", 1, "原"),
    ("Widgets speech-Avery",
     '? ' + BT + '<<nnpc_mummy "Avery">>用<<his>>的方式" : "我用自己的方式">>',
     '? ' + BT + '<<nnpc_mummy "Avery">>用<<his>>的方式' + BT + ' : ' + BT + '我用自己的方式' + BT + '>>', 1, "译"),
    ("Widgets speech-Avery",
     '\t' + BT + 'C.npc.Avery.rage >= 60\n',
     '\tC.npc.Avery.rage >= 60\n', 1, "译"),
    ("Widgets speech-Avery",
     '? ' + BT + '“看看听话会有什么奖励，<<pcpetname "Avery">>？”' + BT + BT,
     ': ' + BT + '“看看听话会有什么奖励，<<pcpetname "Avery">>？”' + BT, 1, "译"),
    ("Avery Valentines Missed Rage Fight Finish",
     '"<<pcpetname "Avery">>">>',
     "\"<<pcpetname 'Avery'>>\">>", 1, "原"),
    ("Mansion Bedroom Avery Dress",
     '开襟羊毛衫<</if>>。"\n',
     '开襟羊毛衫<</if>>。",\n', 1, "译"),
    # ---- Robin ----
    ("Widgets speech-Robin",
     BT + '<<He>>挨了你一下' + BT + ',往后缩去。',
     BT + '<<He>>挨了你一下，往后缩去。' + BT, 1, "译"),
    ("Widgets speech-Robin",
     '\t“看你喝得这么香,我都想把热巧克力摊上的奶换成我自己的奶水了,' + BT + '”<<he>>',
     '\t' + BT + '“看你喝得这么香，我都想把热巧克力摊上的奶换成我自己的奶水了，”<<he>>', 1, "译"),
    ("Widgets speech-Robin",
     '\t"那不是给小宝宝喝的吗？"<<He>>犹豫着问道。\n',
     '\t' + BT + '“那不是给小宝宝喝的吗？”<<He>>犹豫着问道。' + BT + '\n', 1, "译"),
    ("Widgets speech-Robin",
     '\t"你的嘴里好暖和，我太喜欢了！"<<he>><<= either("呻吟道","轻笑着说","咯咯笑着说")>>,\n',
     '\t' + BT + '“你的嘴里好暖和，我太喜欢了！”<<he>><<= either("呻吟道","轻笑着说","咯咯笑着说")>>。' + BT + ',\n', 1, "译"),
    ("Widgets speech-Robin",
     '\t"求你别停，" <<he>>呻吟着,"你这样弄得我好舒服。"\n',
     '\t' + BT + '“求你别停，”<<he>>呻吟着，“你这样弄得我好舒服。”' + BT + '\n', 1, "译"),
    ("Widgets speech-Robin",
     '\t"这感觉……感觉有点淫秽，"<<he>>承认道,脸颊微微泛红。\n',
     '\t' + BT + '“这感觉……感觉有点淫秽，”<<he>>承认道，脸颊微微泛红。' + BT + '\n', 1, "译"),
    ("Widgets speech-Robin",
     '\t"你今天可真黏人。" <<He>><<= either("咯咯笑起来","轻笑出声","微微一笑")>>。\n',
     '\t' + BT + '“你今天可真黏人。”<<He>><<= either("咯咯笑起来","轻笑出声","微微一笑")>>。' + BT + '\n', 1, "译"),
    # ---- 其它 ----
    ("Widgets Text",
     '"你就庆幸自己没办法同时再怀上一次吧。"\n',
     '"你就庆幸自己没办法同时再怀上一次吧。",\n', 1, "原"),
    ("Gwylan Ocean Breeze Ice Cream",
     '<<print either("爸爸", "妈妈")>>',
     "<<print either('爸爸', '妈妈')>>", 2, "译"),
    ("Gwylan Ocean Breeze Ice Cream",
     '<<print either("朋友", "兄弟", "姐妹")>>',
     "<<print either('朋友', '兄弟', '姐妹')>>", 1, "译"),
    ("Gwylan Ritual Sex Widgets",
     '<<= $sexRitual.bondage "bound wrists around" ? : "被绑住的手环绕在" : "手放在">>',
     '<<= $sexRitual.bondage ? "被绑住的手环绕在" : "手放在">>', 1, "原"),
    ("Forest Shop Hunt Widgets",
     '$shopHunt.actors[$_i].state)+"的状态',
     '$shopHunt.actors[$_i].state + "的状态', 6, "译"),
    ("Widgets Wraith",
     '<<set _speechWraith to "你_speak。\\" + _line1 + _line2 + "\\">>',
     '<<set _speechWraith to "你_speak：“" + _line1 + _line2 + "”">>', 1, "译"),
    ("Widgets Wraith",
     '<<set _speechWraith to "你_speak。\\" + _line1 + "\\">>',
     '<<set _speechWraith to "你_speak：“" + _line1 + "”">>', 1, "译"),
    ("Widgets Wraith",
     '<<set _speechWraith to "_speaks。" + "\\"" + _line1 + _line2 + "\\"">>',
     '<<set _speechWraith to "_speaks：“" + _line1 + _line2 + "”">>', 1, "译"),
    ("Widgets Wraith",
     '<<set _speechWraith to "_speaks。\\" + _line1 + "\\">>',
     '<<set _speechWraith to "_speaks：“" + _line1 + "”">>', 1, "译"),
    ("Widgets Bird",
     '<<= _random_clothes。replace("piece of fabric","一块布")>>',
     '<<= _random_clothes.replace("piece of fabric","一块布")>>', 1, "译"),
]

total = 0
miss = []
for pname, old, new, want, cat in FIXES:
    sp = passage_span(data, pname)
    if not sp:
        miss.append((pname, "找不到 passage"))
        continue
    s, e = sp
    body = data[s:e]
    oe, ne = H.escape(old, quote=False), H.escape(new, quote=False)
    c = body.count(oe)
    if c != want:
        miss.append((pname, "命中 %d（应 %d）: %s" % (c, want, old[:60])))
        continue
    body = body.replace(oe, ne)
    data = data[:s] + body + data[e:]
    total += c

# ---- clothesTestingImageGenerate：被翻译的对象键名，按 vanilla 同位置键名恢复 ----
van = open(VANILLA, "rb").read().decode("utf-8", "replace")
CJK_KEY = re.compile(r"^(\s*)([A-Za-z]+[\u4e00-\u9fff]+)\s*[:：]", re.M)
KEY = re.compile(r"^\s*([^\s:：]+)\s*[:：]", re.M)
sp = passage_span(data, "clothesTestingImageGenerate")
vsp = passage_span(van, "clothesTestingImageGenerate")
key_fixed = 0
if sp and vsp:
    s, e = sp
    body = H.unescape(data[s:e])
    vbody = H.unescape(van[vsp[0]:vsp[1]])
    blk_re = re.compile(r"<<set \$characterViewer\.bodyState to \{(.*?)\}>>", re.S)
    cb, vb = list(blk_re.finditer(body)), list(blk_re.finditer(vbody))
    if len(cb) != len(vb):
        miss.append(("clothesTestingImageGenerate", "块数不等 %d/%d" % (len(cb), len(vb))))
    else:
        new_body = body
        for c_m, v_m in reversed(list(zip(cb, vb))):
            ck = KEY.findall(c_m.group(1))
            vk = KEY.findall(v_m.group(1))
            if len(ck) != len(vk):
                miss.append(("clothesTestingImageGenerate", "键数不等 %d/%d" % (len(ck), len(vk))))
                continue
            blk = c_m.group(1)
            ok_blk = True
            for a, b in zip(ck, vk):
                if a != b and not re.search(r"[\u4e00-\u9fff]", a):
                    ok_blk = False
                    miss.append(("clothesTestingImageGenerate", "非中文键不一致 %s/%s" % (a, b)))
            if not ok_blk:
                continue
            for a, b in zip(ck, vk):
                if a != b:
                    n0 = len(re.findall(r"(?m)^(\s*)" + re.escape(a) + r"\s*[:：]", blk))
                    blk = re.sub(r"(?m)^(\s*)" + re.escape(a) + r"\s*[:：]", lambda mm: mm.group(1) + b + ":", blk, count=1)
                    key_fixed += 1 if n0 else 0
            new_body = new_body[:c_m.start(1)] + blk + new_body[c_m.end(1):]
        if key_fixed:
            # 只替换改动过的块：用整段 escape 回写（该 passage 正文无 &quot;/&#39; 特例时安全）
            orig_raw = data[s:e]
            if H.escape(body, quote=False) == orig_raw:
                data = data[:s] + H.escape(new_body, quote=False) + data[e:]
                total += key_fixed
            else:
                miss.append(("clothesTestingImageGenerate", "转义形态不可逆，放弃整段回写"))
                key_fixed = 0

# ---- 标记 ----
anchor = H.escape('<<widget "catcallpregnancy">>', quote=False)
if anchor in data:
    data = data.replace(anchor, H.escape("<!-- [AD10] 修复引擎 parse 后无法编译的宏表达式 -->", quote=False) + anchor, 1)
else:
    miss.append(("标记", "找不到 catcallpregnancy"))

if miss:
    for x in miss:
        print("[AD10] MISS", x)
    print("[AD10] FAIL（未写盘）")
    sys.exit(1)

open(HTML, "wb").write(data.encode("utf-8"))
print("[AD10] 修 %d 处（含对象键名 %d）  passage=%d  OK" % (
    total, key_fixed, len(re.findall(r'<tw-passagedata[^>]*name="', data))))
sys.exit(0)
