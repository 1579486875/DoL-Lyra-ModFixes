"""B04：翻译 152 条 element("span", "英文") 身体变化提示。

句式规律：Your <部位> <变化>。
按 DoL 官方中文风格翻译。
"""
import html as H
import json
import os
import re

WORK = r"E:\TAML\_dol\work"
HTML = os.path.join(WORK, "index_modded6.html")

MAP = {
    # === 生殖器 ===
    "Your penis has grown to a prodigious size.": "你的阴茎长得异常巨大。",
    "Your penis has grown larger.": "你的阴茎变大了。",
    "Your penis has grown to an unremarkable size.": "你的阴茎长到了普通的尺寸。",
    "Your penis has grown, though it's still small.": "你的阴茎长大了些，但依然很小。",
    "Your penis looks like it's recovering.": "你的阴茎似乎在恢复。",
    "Your penis looks like it's been given another chance.": "你的阴茎似乎重获新生。",
    "Your penis has shrunk, though it's still of an impressive size.": "你的阴茎缩小了，但尺寸依然可观。",
    "Your penis has shrunk to an unremarkable size.": "你的阴茎缩小到了普通的尺寸。",
    "Your penis has become smaller.": "你的阴茎变小了。",
    "Your penis has become tiny.": "你的阴茎变得非常小。",
    "Your penis looks like it may shrivel up.": "你的阴茎似乎还会继续萎缩。",
    "Your penis looks like it may never be used properly again.": "你的阴茎似乎再也无法正常使用了。",
    "Your chastity parasite has shrunk, though it still hints at an impressive penis size.": "你的贞操锁寄生虫缩小了，但仍能看出可观的尺寸。",
    "Your chastity parasite has shrunk to an unremarkable size.": "你的贞操锁寄生虫缩小到了普通的尺寸。",
    "Your chastity parasite has become smaller.": "你的贞操锁寄生虫变小了。",
    "Your chastity parasite has become tiny.": "你的贞操锁寄生虫变得非常小。",
    "Your chastity parasite looks like it may shrivel up.": "你的贞操锁寄生虫似乎还会继续萎缩。",
    "Your chastity parasite looks like it's barely concealing anything.": "你的贞操锁寄生虫几乎遮不住任何东西了。",

    # === 胸部 ===
    "Your large breasts feel heavy and might get in the way.": "你丰满的胸部沉甸甸的，可能会碍事。",
    "Your large breasts feel heavy and impressive.": "你丰满的胸部沉甸甸的，十分可观。",
    "Your breasts feel heavy.": "你的胸部感觉沉重。",
    "Your breasts feel a little heavier.": "你的胸部感觉沉了一点。",
    "Your small breasts will be obvious to those around you.": "你小巧的胸部在旁人眼里会很明显。",
    "Your small breasts might be obvious to others.": "你小巧的胸部在别人看来可能会很明显。",
    "Your chest feels odd; it might be growing.": "你的胸口感觉怪怪的，也许正在发育。",
    "Your large breasts feel lighter, but are still very large.": "你丰满的胸部轻了些，但依然很大。",
    "Your breasts feel light and are looking less impressive.": "你的胸部感觉变轻，也不那么显眼了。",
    "Your breasts feel lighter.": "你的胸部感觉轻了些。",
    "Your small breasts feel a little lighter.": "你小巧的胸部感觉轻了一点。",
    "Your small breasts look less obvious.": "你小巧的胸部不那么显眼了。",
    "Your chest looks flatter.": "你的胸口看起来平坦了些。",
    "Your chest looks flat.": "你的胸口看起来是平的。",

    # === 臀部 ===
    "Your large butt has become even larger.": "你丰满的臀部变得更大了。",
    "Your butt feels heavy.": "你的臀部感觉沉重。",
    "Your butt feels plump.": "你的臀部感觉丰腴。",
    "Your butt feels round.": "你的臀部感觉圆润。",
    "Your butt feels plush.": "你的臀部感觉柔软饱满。",
    "Your butt has gained a little weight.": "你的臀部胖了一点。",
    "Your small butt sticks out more than you remember.": "你小巧的臀部比你记忆中更翘了。",
    "Your butt doesn't feel so small any more.": "你的臀部感觉不再那么小了。",
    "Your large butt feels a bit lighter.": "你丰满的臀部感觉轻了一点。",
    "Your butt feels lighter.": "你的臀部感觉轻了些。",
    "Your butt isn't quite as cushioned as before.": "你的臀部不像以前那么柔软了。",
    "Your butt has lost weight.": "你的臀部瘦了些。",
    "Your butt feels a lot sleeker.": "你的臀部感觉紧致多了。",
    "Your butt feels small.": "你的臀部感觉小巧。",
    "Your butt feels tiny.": "你的臀部感觉非常小。",

    # === 性格/行为 ===
    "You've become too submissive to adopt a bratty demeanour in conversation.": "你变得太顺从了，无法在对话中摆出刁蛮的态度。",
    "You've become too defiant to adopt a meek demeanour in conversation.": "你变得太叛逆了，无法在对话中摆出温顺的态度。",
    "You are no longer so masochistic and can only be considered a": "你不再那么受虐成性，只能算是",
    "You are no longer so sadistic and can only be considered a": "你不再那么施虐成性，只能算是",

    # === 药物 ===
    "You take your daily pills.": "你服用了今天的药片。",
    "You have run out of some of them.": "其中一些已经用完了。",
    "using the last of it.": "用掉了最后一点。",
    "but used the last of it.": "但用掉了最后一点。",

    # === 心理 ===
    "Your thoughts wander over the attacks you've suffered. You shiver.": "你的思绪飘向遭受过的袭击。你打了个寒颤。",
    "Your thoughts turn to the attacks you've suffered. A thrill follows, unbeckoned.": "你的思绪转向遭受过的袭击。一阵战栗不请自来。",
    "Your body yearns for more abuse.": "你的身体渴望着更多虐待。",
    "Your body craves more abuse.": "你的身体渴求更多虐待。",
    "Your thoughts turn to the pain you've inflicted. You shiver.": "你的思绪转向你造成的痛苦。你打了个寒颤。",
    "Your thoughts turn to the pain you've inflicted. A thrill follows, unbeckoned.": "你的思绪转向你造成的痛苦。一阵战栗不请自来。",
    "You yearn to hurt others.": "你渴望着伤害他人。",
    "If they want to play rough, so be it.": "既然他们想玩硬的，那就来吧。",
    "You feel an odd sense of yearning grow within you, and you are filled with a deep desire. An unbearable lust soon takes hold.": "你感到内心涌起一种奇异的渴望，被深沉的欲望填满。难以忍受的情欲很快占据了全身。",

    # === 学校流言 ===
    "Everyone at school has heard of your unique genitalia, including the teachers.": "学校里所有人都听说过你独特的生殖器，连老师都知道。",
    "Rumours of your unique genitalia have spread throughout the school.": "关于你独特生殖器的传闻传遍了整个学校。",
    "It sounds far-fetched to many, but the school is rife with gossip about a student with both boy and girl parts.": "很多人觉得难以置信，但学校里盛传着一个同时拥有男女器官的学生的流言。",
    "Rumours of a student with both boy and girl parts are spreading through the school.": "关于一个同时拥有男女器官的学生的传闻正在校内传播。",
    "A few cliques at school have begun whispering about a student with both boy and girl parts.": "学校里几个小圈子开始私下议论一个同时拥有男女器官的学生。",

    # === 其他 ===
    "Your spray was accurate. You didn't need to use a full cartridge, saving ammo.": "你的喷雾精准命中。你不必用掉整罐，节省了弹药。",
    "Sex toys are becoming more popular throughout town.": "性玩具在小镇上越来越流行了。",
    "You have a book severely overdue, and the police have been informed.": "你有一本书严重逾期，警方已被通知。",
    "You have a book overdue and have incurred delinquency.": "你有一本书逾期未还，记了违规。",
    "A fell mist hangs over Elk Street.": "麋鹿街笼罩着一层阴森的雾气。",
    "The slime in your ear punishes you for failing to complete your task.": "你耳中的史莱姆因为你没完成任务而惩罚你。",
    "The slime in your ear is upset you were unable to complete what you said you would do.": "你耳中的史莱姆因为你没能做到说过的事而恼怒。",
    "You feel a familiar emptiness return in your womb.": "你感到子宫里又泛起熟悉的空虚感。",
    "Your skulduggery has improved to": "你的诡计提升到了",
    "whirring with guilt and anxiety.": "在内疚与焦虑中飞转。",

    # === 恶魔/天使 ===
    "Your blackened wings turn blacker still. Your shattered halo fades. Horns sprout from your scalp and a tail sprouts from your lower back. Your sense of loss is replaced with a desire for revenge.": "你漆黑的羽翼变得更黑。破碎的光环消散了。犄角从头顶钻出，尾巴从后腰长出。失落感被复仇的欲望所取代。",
    "You are pure and feel determined to keep it that way.": "你是纯洁的，并决心保持下去。",
    "You feel a weight lift from your shoulders.": "你感到肩上的重担卸下了。",
    "A golden light shines down on you.": "一道金色的光芒洒落在你身上。",
    "You feel a soothing warmth in your back.": "你感到后背传来一阵舒缓的暖意。",
    "You feel lighter. Your new wings caress your face.": "你感觉轻飘飘的。新生的羽翼轻抚着你的脸庞。",
    "You feel soiled.": "你感到被玷污了。",
    "You feel dirty.": "你感到肮脏。",
    "You feel a weight bear down on you.": "你感到有重担压在身上。",
    "The light above you fades.": "头顶的光芒暗淡下去。",
    "The soothing warmth in your back fades.": "后背的暖意消散了。",
    "Your wings fade away.": "你的羽翼消散了。",
    "You feel an invisible light burn away your impurity.": "你感到一道无形的光烧去了你的污秽。",
    "Your horns recede.": "你的犄角缩回去了。",
    "Your tail recedes.": "你的尾巴缩回去了。",
    "The burning in your back ceases.": "后背的灼烧感停止了。",
    "Your wings recede.": "你的羽翼缩回去了。",

    # === 狼 ===
    "You have a strange toothache.": "你的牙齿莫名地疼。",
    "You have a strange toothache. A beetle crawls by. You resist the urge to pounce.": "你的牙齿莫名地疼。一只甲虫爬过。你忍住扑上去的冲动。",
    "You feel something on your head. You reach up and tug, but it hurts. You have a new pair of wolf ears.": "你感觉头上有什么东西。你伸手去拽，但很疼。你长出了一对狼耳。",
    "You also notice long and fluffy hair has grown in your pubic area.": "你还注意到阴部长出了又长又蓬松的毛。",
    "Your bottom feels heavier than usual. You reach behind you and feel your new wolf tail.": "你的臀部比平时沉重。你伸手向后，摸到了新长出的狼尾。",
    "Your lower back has stopped itching.": "你的后腰不再发痒了。",
    "Your balance feels different. Your wolf tail has disappeared.": "你的平衡感变了。你的狼尾消失了。",

    # === 猫 ===
    "Your scalp itches.": "你的头皮发痒。",
    "Your scalp twitches. You reach up and feel your new pair of cat ears.": "你的头皮抽动着。你伸手摸到了一对新长出的猫耳。",
    "Your bottom feels weighty, yet perfectly balanced. You reach behind and feel your new cat tail.": "你的臀部沉甸甸的，却出奇地平衡。你伸手向后，摸到了新长出的猫尾。",
    "Your eyes itch.": "你的眼睛发痒。",
    "Your eyes water from a burning sensation around the pupil.": "你的瞳孔周围传来灼烧感，眼睛直淌泪。",
    "Your eyes burn, likely due to some sort of allergy. You can barely keep them open.": "你的眼睛灼痛，大概是某种过敏。你几乎睁不开眼。",
    "Your eyes no longer burn. Despite the darkness of the early morning, you are able to pick up every detail of the scenery around you.": "你的眼睛不再灼痛。尽管清晨天色昏暗，你却能看清周围景物的每一处细节。",
    "Your scalp no longer itches.": "你的头皮不再发痒了。",
    "Your cat ears have disappeared.": "你的猫耳消失了。",
    "The itching in your lower back stops.": "你后腰的瘙痒停止了。",
    "Your cat tail disappears.": "你的猫尾消失了。",
    "Your eyes no longer itch; it must have been an allergy.": "你的眼睛不再发痒，想必是过敏。",
    "Your eyes sense less detail of your surroundings.": "你眼中周围环境的细节变少了。",
    "Your surroundings appear darker than before.": "周围看起来比以前更暗了。",

    # === 牛 ===
    "You have a strange urge to munch grass.": "你莫名地想嚼草。",
    "Your scalp itches. You reach up and find that a pair of small horns have sprouted.": "你的头皮发痒。你伸手去摸，发现长出了一对小犄角。",
    "Your ears tingle.": "你的耳朵发麻。",
    "Your ears itch. You reach up to scratch them and find them much bigger than you expected. You've grown a pair of cow ears.": "你的耳朵发痒。你伸手去挠，发现它们比你预想的要大得多。你长出了一对牛耳。",
    "Your lower back tingles.": "你的后腰发麻。",
    "Your bottom feels heavier than usual. You reach behind you and feel your new cow tail. You suppress the urge to moo.": "你的臀部比平时沉重。你伸手向后，摸到了新长出的牛尾。你忍住了哞哞叫的冲动。",
    "Grass no longer looks so tasty.": "草看起来不再那么美味了。",
    "Your small horns have disappeared.": "你的小犄角消失了。",
    "Your ears no longer tingle.": "你的耳朵不再发麻了。",
    "Your cow ears have disappeared.": "你的牛耳消失了。",
    "Your lower back has stopped tingling.": "你的后腰不再发麻了。",
    "Your balance feels different. Your cow tail has disappeared.": "你的平衡感变了。你的牛尾消失了。",

    # === 鸟/鹰身 ===
    "Your vision feels sharper.": "你的视力变得更锐利。",
    "Your eyes feel strange. Your vision has improved.": "你的眼睛感觉怪怪的。视力提升了。",
    "Your bottom feels lighter. You reach behind you and grasp a feathered tail. Small feathers cover your neck.": "你的臀部感觉轻了。你伸手向后，抓住了一条羽尾。细小的羽毛覆上了你的脖颈。",
    "Your vision has returned to normal.": "你的视力恢复正常了。",
    "Your vision is no longer so sharp.": "你的视力不再那么锐利了。",
    "The itching in your lower back and neck both stop, and you no longer crave a partner so feverishly.": "后腰和脖颈的瘙痒同时停止了，你也不再那样狂热地渴求伴侣。",
    "Your feathered tail has disappeared, along with the feathers on your neck.": "你的羽尾消失了，脖颈上的羽毛也不见了。",
    "Your wings have grown some new feathers.": "你的羽翼长出了些新羽毛。",
    "The familiar feeling of soft feathers fills you with hope.": "那熟悉的柔软羽毛让你满怀希望。",

    # === 狐 ===
    "You have a strange toothache, and your eyes feel a little sharper. You have the urge to steal something.": "你的牙齿莫名地疼，眼睛也锐利了些。你有一股想偷东西的冲动。",
    "Your mouth and eyes feel different. You explore your mouth and yip as your tongue presses against your new fangs.": "你的嘴和眼睛感觉不同了。你探了探口腔，舌头碰到新长出的獠牙时发出一声尖啸。",
    "You feel something on your head. You reach up and touch your new pair of fox ears, and they wiggle in response.": "你感觉头上有什么东西。你伸手摸到一对新长出的狐耳，它们应声抖动。",
    "Your lower back itches. You have the urge to let someone scratch it. You also notice strange discolouration around your eyes.": "你的后腰发痒。你想找人挠一挠。你还注意到眼周有奇怪的变色。",
    "Your bottom feels heavier than usual. You give it a wiggle and feel your new fox tail. It's extremely comforting to touch.": "你的臀部比平时沉重。你扭了扭，摸到了新长出的狐尾。摸起来非常舒服。",
    "Your fangs have turned into regular teeth, and your eyesight feels dull.": "你的獠牙变回了普通的牙齿，视力也变得迟钝。",
    "Your scalp no longer itches, and you no longer crave a partner so feverishly.": "你的头皮不再发痒，也不再那样狂热地渴求伴侣。",
    "Your fox ears have disappeared.": "你的狐耳消失了。",
    "Your lower back has stopped itching, and the discolouration around your eyes has vanished.": "你的后腰不再发痒，眼周的变色也消失了。",
    "Your balance feels different. Your fox tail has disappeared.": "你的平衡感变了。你的狐尾消失了。",
    "Your mouth feels different. You explore your mouth and wince as your tongue presses against your new fangs.": "你的嘴感觉不同了。你探了探口腔，舌头碰到新长出的獠牙时疼得缩了一下。",
    "Your fangs have turned into regular teeth.": "你的獠牙变回了普通的牙齿。",
    "Your lower back itches.": "你的后腰发痒。",
    "Your toothache has stopped.": "你的牙痛停止了。",
    "Your bottom feels weighty, yet perfectly balanced. You reach behind and feel your new cat tail.": "你的臀部沉甸甸的，却出奇地平衡。你伸手向后，摸到了新长出的猫尾。",
}

print(f"翻译表 {len(MAP)} 条")

data = open(HTML, "rb").read().decode("utf-8", "replace")
if len(re.findall(r"<tw-passagedata", data)) < 10000:
    print("❌ index 不是明文形态")
    raise SystemExit(1)

n = 0
miss = []
for en, cn in MAP.items():
    # 只替换 element("span", "xxx") 里的，避免误伤其他地方
    old1 = 'element("span", "' + en + '"'
    new1 = 'element("span", "' + cn + '"'
    if old1 in data:
        c = data.count(old1)
        data = data.replace(old1, new1)
        n += c
    else:
        # 可能带颜色参数
        old2 = '"' + en + '"'
        if old2 in data:
            c = data.count(old2)
            data = data.replace(old2, '"' + cn + '"')
            n += c
        else:
            miss.append(en)

open(HTML, "wb").write(data.encode("utf-8"))
print(f"✅ 替换 {n} 处，未命中 {len(miss)} 条")
for x in miss[:10]:
    print(f"  ⚠️ {x[:80]!r}")

# 校验
g = open(HTML, "rb").read().decode("utf-8", "replace")
print(f"\npassage: {len(re.findall(r'<tw-passagedata', g))}")
print(f"Your eyes itch 残留: {g.count('Your eyes itch')}")
print(f"你的眼睛发痒: {g.count('你的眼睛发痒')}")
