"""第 17 轮：翻译 i18n 完全未覆盖的 6 个 Pub Avery passage。

只替换正文英文，保留全部 <<宏>>、$变量、HTML 标签。
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

# (passage 名, 原文, 译文) —— 整段替换，最可靠
PASSAGES = {
"Pub Avery Nod Note": (
'''<<effects>>
Reworked
You nod, and Landry leans back with a smile. "Anything else?"
<br><br>

<<landryoptions>>
<<getouticon>><<link [[Leave|Pub]]>><<endevent>><</link>>
<br>''',
'''<<effects>>
你点了点头，兰德里向后一靠，露出笑容。"还有别的事吗？"
<br><br>

<<landryoptions>>
<<getouticon>><<link [[离开|Pub]]>><<endevent>><</link>>
<br>'''),

"Pub Avery Nod Point": (
'''<<effects>>

<<if $speech_attitude is "meek">>
	"That's very generous of you," you say. "But Avery is also generous. And rich. You want me to betray <<nnpc_him Avery>>?"
<<elseif $speech_attitude is "bratty">>
	"You want me to betray Avery for a sum <<nnpc_he Avery>>'d find down <<nnpc_his Avery>> sofa?" you ask.
<<else>>
	"That's not much money for Avery," you say.
<</if>>
<br><br>

Landry laughs. "I know. Wasn't my decision, that reward, believe me." <<He>> glances towards the front of the pub. "The £10000 would be from some friends of mine. They're a bit out of touch I'm afraid. But they're strong. The sort your Bailey has to tiptoe around, or risk being crushed by. They have things, and do things, money can't buy. Friends like that would be good to have, no?"
<br><br>

"No pressure. Just keep an eye out." <<He>> leans back. "Anything else?"
<br><br>

<<landryoptions>>
<<getouticon>><<link [[Leave|Pub]]>><<endevent>><</link>>
<br>''',
'''<<effects>>

<<if $speech_attitude is "meek">>
	"您真是太大方了，"你说道。"但艾弗里也很慷慨，而且很有钱。您是想让我背叛<<nnpc_him Avery>>吗？"
<<elseif $speech_attitude is "bratty">>
	"您想让我为了这点钱就背叛艾弗里？这数目<<nnpc_he Avery>>在沙发缝里都能翻出来吧？"你问道。
<<else>>
	"对艾弗里来说，这点钱可不算多，"你说道。
<</if>>
<br><br>

兰德里笑了。"我知道。这个数目可不是我定的，相信我。"<<He>>朝酒馆门口瞥了一眼。"那一万英镑会由我的一些朋友出。恕我直言，他们有点跟不上时代了。但他们很强。强到你那位贝利都得小心翼翼绕着走，否则就会被打得粉碎。他们手里有些东西，做的事也是钱买不来的。这样的朋友，结交一下不坏，对吧？"
<br><br>

"没有压力，留意着就行。"<<He>>向后一靠。"还有别的事吗？"
<br><br>

<<landryoptions>>
<<getouticon>><<link [[离开|Pub]]>><<endevent>><</link>>
<br>'''),

"Pub Avery Stones Give": (
'''<<effects>>

You reach for the stones. A strength runs through your fingers as you touch them. Landry observes you, and raises an eyebrow.
<br><br>
"You have something for me?"
<br><br>

<<link [[Give Landry the stones|Pub Avery Stones 2]]>><</link>>
<br>
<<link [[Reconsider|Pub Avery Stones Reconsider]]>><</link>>
<br>''',
'''<<effects>>

你伸手去拿那些石头。指尖触到的瞬间，一股力量顺着手臂流淌而过。兰德里观察着你，挑了挑眉。
<br><br>
"你有东西要给我？"
<br><br>

<<link [[把石头交给兰德里|Pub Avery Stones 2]]>><</link>>
<br>
<<link [[再考虑一下|Pub Avery Stones Reconsider]]>><</link>>
<br>'''),

"Pub Avery Stones Reconsider": (
'''<<effects>>

You shake your head. Landry observes you, <<his>> face giving nothing away.
<br><br>

<<landryoptions>>
<<getouticon>><<link [[Leave|Pub]]>><<endevent>><</link>>
<br>''',
'''<<effects>>

你摇了摇头。兰德里看着你，<<his>>脸上什么也看不出来。
<br><br>

<<landryoptions>>
<<getouticon>><<link [[离开|Pub]]>><<endevent>><</link>>
<br>'''),

"Pub Avery Stones 2": (
'''<<effects>>

<<set $auriga_artefact to "Landry">>

Landry just looks at the stones for a moment, transfixed as if in wonder. "To be honest," <<he>> says. "I didn't think you'd find them." <<He>> reaches forward, then catches <<himself>>. <<He>> reaches into <<his>> pocket, and produces a thick envelope. <<He>> pushes it across the table. "For services rendered. I'll also put in a good word for you." <<He>> smiles. "You've done a very good thing."
<br><br>

<<He>> reaches for the bones, but hesitates. "Those really are bones." <<He>> peers at them. "Let's hope they're from an animal, eh?" <<He>> reaches into <<his>> pocket, and produces a magnifying glass. <<His>> smile broadens. "There's a code etched into the bone. As I thought. Wish they had hidden it somewhere less gristly."
<br><br>

You've gained <<moneyGain 10000>>.
<br><br>

Landry seals the wishing stones within a plastic bag. "I'll need help to analyse them more closely. Anything else?"
<br><br>
<<landryoptions>>
<<getouticon>><<link [[Leave|Pub]]>><<endevent>><</link>>
<br>''',
'''<<effects>>

<<set $auriga_artefact to "Landry">>

兰德里只是盯着那些石头看了一会儿，像被施了定身术般出神。"说实话，"<<he>>说道，"我没想到你真能找到它们。"<<He>>伸手向前，又停住了。<<He>>把手伸进口袋，掏出一个厚厚的信封，推过桌面。"这是报酬。我还会替你说几句好话。"<<He>>笑了笑。"你做了件大好事。"
<br><br>

<<He>>伸手去拿那些骨头，却犹豫了。"这可真是骨头啊。"<<He>>凑近细看。"但愿是动物的，嗯？"<<He>>从口袋里掏出一枚放大镜，笑容更深了。"骨头上刻着一串密码。果然如此。真希望他们把它藏在没那么渗人的地方。"
<br><br>

你获得了<<moneyGain 10000>>。
<br><br>

兰德里把许愿石封进一个塑料袋。"要仔细分析还得找人帮忙。还有别的事吗？"
<br><br>
<<landryoptions>>
<<getouticon>><<link [[离开|Pub]]>><<endevent>><</link>>
<br>'''),
}


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    ok = 0
    fail = []

    PAT = re.compile(r'(<tw-passagedata[^>]*name="([^"]+)"[^>]*>)(.*?)(</tw-passagedata>)', re.S)

    def repl(m):
        nonlocal ok
        open_tag, pname, body_esc, close_tag = m.group(1), m.group(2), m.group(3), m.group(4)
        pname_u = H.unescape(pname)
        if pname_u not in PASSAGES:
            return m.group(0)
        old, new = PASSAGES[pname_u]
        body = H.unescape(body_esc)
        if old in body:
            body = body.replace(old, new, 1)
            ok += 1
            print(f"  ✅ [{pname_u}]")
            return open_tag + H.escape(body, quote=False) + close_tag
        # 已经译过？
        if new[:40] in body:
            print(f"  ⏭  [{pname_u}] 已是译文")
            return m.group(0)
        fail.append(pname_u)
        return m.group(0)

    new_data = PAT.sub(repl, data)
    print(f"\n翻译 {ok} / {len(PASSAGES)}")
    for f in fail:
        print(f"  ❌ [{f}] 未匹配")

    open(HTML, "wb").write(new_data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
