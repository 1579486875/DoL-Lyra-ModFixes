"""第 18 轮：翻译 Pub Avery Fake Stones + 移除多余的 */ 注释结束符。"""
import html as H
import os
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

OLD = '''<<effects>>

<<set $avery_mansion.fake_stones to 2>>
<<if $auriga_artefact is "Landry">>
	<<if $speech_attitude is "meek">>
		"I hate to be a bother," you say. "But do you know how I could replace the wishing stones? Avery can be hard to deal with, and it would be easier if they were replaced with a fake."
	<<elseif $speech_attitude is "bratty">>
		"Avery will discover the stones' absence sooner or later," you say. "Could be trouble for me. Know any way I could fool <<nnpc_him Avery>>?"
	<<else>>
		"A forgery of the stones would be useful," you say. "I could leave them in the vault instead, and keep Avery in the dark for longer."
	<</if>>
	<br><br>
	Landry smiles, reaches beneath the table, and produces the wishing stones.
	<br><br>
	"These are fake," <<he>> says with a satisfied smile. "Good, aren't they?" They do appear identical, as far as you can tell. "Note that they're not a perfect copy. We only had those pictures to go on. But it should fool Avery and co well enough."
	<br><br>
<<else>>
	<<if $speech_attitude is "meek">>
		"I found the wishing stones you wanted," you say. "But I'd be in trouble if Avery sees them gone. Do you have something I could replace them with?"
	<<elseif $speech_attitude is "bratty">>
		"I know where those stones are," you say. "Gimme something to replace them with, and they're all yours."
	<<else>>
		"I found the stones," you say. "I just need something to replace them with."
	<</if>>
	<br><br>
	Landry smiles, reaches beneath the table, and produces a copy of the wishing stones. Identical, as far as you can tell.
	<br><br>

	"It pays to prepare," <<he>> says, giving you a satisfied smile. "Note that they're not a perfect copy. We only had those pictures to go on. But it should fool Avery and co well enough."
	<br><br>
<</if>>

You reach for the fake stones. Landry's smile falters as you touch them. "Be gentle with them," <<he>> says. "We used illegal components. Had to. Damage could release nasty chemicals into the air. They'd be hard to replace as well." <<He>> leans back. "Anything else?"
<br><br>

<<landryoptions>>
<<getouticon>><<link [[Leave|Pub]]>><<endevent>><</link>>
<br>
 */'''

NEW = '''<<effects>>

<<set $avery_mansion.fake_stones to 2>>
<<if $auriga_artefact is "Landry">>
	<<if $speech_attitude is "meek">>
		"我很不想麻烦您，"你说道。"但您知道该怎么替换那些许愿石吗？艾弗里很难对付，如果能换成赝品，事情会好办得多。"
	<<elseif $speech_attitude is "bratty">>
		"艾弗里迟早会发现石头不见了，"你说道。"那对我可是麻烦。您有办法糊弄<<nnpc_him Avery>>吗？"
	<<else>>
		"如果能仿造那些石头就好了，"你说道。"我可以把赝品放回保险库，让艾弗里更久蒙在鼓里。"
	<</if>>
	<br><br>
	兰德里笑了笑，把手伸到桌下，取出那些许愿石。
	<br><br>
	"这些是假的，"<<he>>带着满意的笑容说道。"做得不错吧？"就你所能分辨的，它们看起来一模一样。"注意，并不是完美的复制。我们只有那几张照片作参考。但骗过艾弗里那伙人足够了。"
	<br><br>
<<else>>
	<<if $speech_attitude is "meek">>
		"我找到您要的许愿石了，"你说道。"但如果艾弗里发现它们不见了，我就麻烦了。您有什么东西能让我替换它们吗？"
	<<elseif $speech_attitude is "bratty">>
		"我知道那些石头在哪，"你说道。"给我个替换的东西，它们就归您了。"
	<<else>>
		"我找到石头了，"你说道。"我只需要一个替换品。"
	<</if>>
	<br><br>
	兰德里笑了笑，把手伸到桌下，取出一份许愿石的复制品。就你所能分辨的，一模一样。
	<br><br>

	"有备无患，"<<he>>说道，给了你一个满意的笑容。"注意，并不是完美的复制。我们只有那几张照片作参考。但骗过艾弗里那伙人足够了。"
	<br><br>
<</if>>

你伸手去拿那些假石头。兰德里在你触碰时笑容一滞。"轻一点，"<<he>>说道。"我们用了违禁材料。不得不用。弄坏了可能会释放出有害气体。而且也很难再做一个了。"<<He>>向后一靠。"还有别的事吗？"
<br><br>

<<landryoptions>>
<<getouticon>><<link [[离开|Pub]]>><<endevent>><</link>>
<br>'''


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    e_old = H.escape(OLD, quote=False)
    e_new = H.escape(NEW, quote=False)

    if e_old in data:
        data = data.replace(e_old, e_new, 1)
        print("✅ Pub Avery Fake Stones 已翻译 + 移除多余 */")
    elif OLD in data:
        data = data.replace(OLD, NEW, 1)
        print("✅ Pub Avery Fake Stones 已翻译 + 移除多余 */（未转义形态）")
    elif NEW[:60] in data or H.escape(NEW[:60], quote=False) in data:
        print("⏭ 已是译文")
    else:
        print("❌ 未匹配，需人工检查")

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
