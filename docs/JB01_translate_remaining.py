"""翻译 JA02 找出的 39 句残留英文剧情。

这些句子在全库唯一，直接字符串替换即可（含 HTML 转义形态兼容）。
跳过 [Widgets] Expected a second parameter（SugarCube 运行时错误信息，不该翻）。
"""
import os
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

PAIRS = [
    ("The nurse helps you sit and calls out for assistance.",
     "护士扶你坐起，并大声呼救。"),
    ("There's a small cake sat on the windowsill with a note attached.",
     "窗台上放着一个小蛋糕，上面附着一张纸条。"),
    ("You enter the orphanage and head to your room.",
     "你走进孤儿院，朝自己的房间走去。"),
    ("Harper stares at you across the desk.",
     "哈珀隔着桌子盯着你。"),
    ("You tell Gwylan you need to stop.",
     "你告诉格威岚，你需要停下来。"),
    ("The gloom closes in on you.",
     "阴霾向你围拢过来。"),
    ("You chat with some students you recognise from your classes.",
     "你和几个在课上见过的学生聊了几句。"),
    ("An unlit fireplace sits in the centre of the clearing.",
     "空地中央有一处没点火的壁炉。"),
    ("You see several students hanging out on and around it.",
     "你看见几个学生在那上面和周围闲荡。"),
    ("You are swimming in the middle of the lake near the dock.",
     "你在码头附近的湖心游泳。"),
    ("It dulls the sound of the rain above.",
     "它让头顶的雨声变得沉闷。"),
    ("You find an empty spot to lie on and close your eyes.",
     "你找到一处空地躺下，闭上了眼睛。"),
    ("You grab your basket and start walking back towards the farm.",
     "你抓起篮子，朝农场的方向走回去。"),
    ("You head to the exit, where Sam is seeing off guests.",
     "你走向出口，山姆正在那里送客。"),
    ("For now, it fills with rainwater.",
     "眼下，它积满了雨水。"),
    ("The workers must be getting close to breaching the spring.",
     "工人们应该快要挖到泉眼了。"),
    ("Winter returns to the class, and sees you in your undressed state.",
     "温特回到教室，看见了你衣衫不整的样子。"),
    ("The teacher conceals your body with a towel while freeing you from the pillory.",
     "老师用毛巾遮住你的身体，同时把你从枷锁里放了下来。"),
    ("You dress yourself with shaking fingers, doing your best to ignore the disappointed heckling from the class.",
     "你用发抖的手指穿好衣服，尽量不去理会班上失望的起哄声。"),
    ("You walk back to your seat.",
     "你走回自己的座位。"),
    ("Sirris doesn't say anything, but refusing a teacher won't reflect well on you.",
     "茜里斯什么也没说，但拒绝老师不会给你留下好印象。"),
    ("It grows and spreads through your body, concentrated on your loins.",
     "它在你体内生长蔓延，集中在小腹一带。"),
    ("Within moments, your cheeks are flushed and you find yourself squirming with desire.",
     "转眼间，你双颊泛红，身体不由自主地因欲望而扭动。"),
    ("That dose must have been contaminated by a concentrated aphrodisiac.",
     "那一剂药一定是被高浓度的春药污染了。"),
    ("You sit back and admire your work.",
     "你向后一靠，欣赏起自己的作品。"),
    ("You feel a strange heat just beneath your skin.",
     "你感到皮肤下泛起一阵异样的燥热。"),
    ("You are near the beach outside town.",
     "你在镇外的海滩附近。"),
    ("You can see the town in the distance.",
     "你能望见远处的镇子。"),
    ("You are swimming in the sea.",
     "你在海里游泳。"),
    ("You swim to the surface and climb onto the bank.",
     "你游到水面，爬上了岸边。"),
    ("You repress the urge to spit in their holy water.",
     "你忍住了往他们的圣水里吐口水的冲动。"),
    ("It's a brass statuette, moulded in the shape of an eagle.",
     "那是一尊黄铜小雕像，铸成了鹰的形状。"),
    ("You caught your hand on its beak.",
     "你的手被它的喙划了一下。"),
    ("You reach in again, gingerly this time, and wrap your fingers around something cool and hard.",
     "你再次把手伸进去，这次小心翼翼，手指握住了一个冰凉坚硬的东西。"),
    ("You bring it out into the light.",
     "你把它拿到光亮处。"),
    ("You find a quiet spot and examine the camera.",
     "你找了个安静的角落，仔细查看这台相机。"),
    ("Are you coming trick-or-treating with us?",
     "你要不要和我们一起去讨糖？"),
    # 带 HTML 标签的
    ("You are swimming in the middle of the lake near the dock.", "你在码头附近的湖心游泳。"),
]


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    ok = 0
    miss = []
    for en, cn in PAIRS:
        if en in data:
            n = data.count(en)
            data = data.replace(en, cn)
            ok += 1
            print(f"  ✅ {en[:60]!r}  ({n} 处)")
        else:
            miss.append(en)

    print(f"\n翻译 {ok} / {len(PAIRS)}")
    for m in miss:
        print(f"  ❌ {m[:80]!r}")

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
