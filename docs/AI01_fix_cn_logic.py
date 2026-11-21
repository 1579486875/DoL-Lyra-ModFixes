"""AI01（第12轮-2）：修社区汉化 issue 报告、经核实我们的包同样存在的逻辑 bug（幂等）。

只读参考：github.com/Eltirosto/Degrees-of-Lewdity-Chinese-Localization 的 issue（未向其发任何 PR/issue/评论）。
修法全部是 ① 保意图 —— 显示文字保持汉化，判断处同时接受英文原值与汉化值（新旧存档都兼容）。

  #579 钓鱼开场报错：<<fishingMinigameStartText>> 取 behaviors[x].initialActionCN，
       官方汉化只给 6 种鱼行为里的 4 种加了这个字段（runner / panicked 没有）→ undefined.replace → 鲱鱼等开场红字。
       改为「有中文用中文，没有就退回原版 initialAction」（后面的 .replace 链本来就负责把 run/thrash/idle 译成中文）。
  #583 逃离地下农场时半人马救援/亲吻选项消失：<<livestock_horse>> 的 _text_output 被汉化成「半人马」，
       而 $remyEscapeSteed is "centaur" 判断用英文 → 永远为假。同类：Livestock Caught 的 "stallion"。
  同类（本轮全量扫描新增，社区未报）：
       Temple Confess Sydney Sex   _sydtext is "Sydney"（赋值已是「悉尼」）→「悉尼停了下来」分支永不出现
       Hospital Keycard Caught      _text_output is "meat"（<<underworld_nickname>> 已输出「肥羊」）→ 台词分支错
       Pregnancy ultrasound 2       _type is "harpy"（赋值已是「哈比」）→ 哈比胎儿「两只胳膊」描述缺失
       Widgets Pub Fame             password[2] is "the blood moon"（密码数组已改为中文语序，特殊值是「之下」）
"""
import html as H
import os
import re
import sys

HTML = os.environ.get("DOL_HTML") or r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")
if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[AI01] index 形态异常")
    sys.exit(1)
MARK = "[AI01]"
if MARK in H.unescape(data):
    print("[AI01] 已存在，跳过")
    sys.exit(0)


def span(name):
    m = re.search(r'<tw-passagedata\s+[^>]*name="' + re.escape(name) + r'"[^>]*>', data)
    return (m.end(), data.find("</tw-passagedata>", m.end())) if m else None


FIXES = [
    ("Widgets Fishing Minigame",
     "<<set _initialMinigameAction to setup.fishingMinigame.behaviors[setup.fishing.lootTables.fish[$fishingHookedFish.type].minigame.behavior].initialActionCN>>",
     "<<set _initialMinigameAction to setup.fishingMinigame.behaviors[setup.fishing.lootTables.fish[$fishingHookedFish.type].minigame.behavior].initialActionCN"
     " || setup.fishingMinigame.behaviors[setup.fishing.lootTables.fish[$fishingHookedFish.type].minigame.behavior].initialAction>>", 1),
    ("Livestock Escape",
     '<<if $remyEscapeSteed is "centaur">>',
     '<<if $remyEscapeSteed is "centaur" or $remyEscapeSteed is "半人马">>', 1),
    ("Livestock Caught",
     '<<if $remyEscapeSteed is "centaur">>',
     '<<if $remyEscapeSteed is "centaur" or $remyEscapeSteed is "半人马">>', 1),
    ("Livestock Caught",
     '<<if $remyEscapeSteed is "stallion">>',
     '<<if $remyEscapeSteed is "stallion" or $remyEscapeSteed is "公马">>', 1),
    ("Temple Confess Sydney Sex",
     '<<elseif _sydtext is "Sydney">>',
     '<<elseif _sydtext is "Sydney" or _sydtext is "悉尼">>', 1),
    ("Hospital Keycard Caught",
     '<<if _text_output is "meat">>',
     '<<if _text_output is "meat" or _text_output is "肥羊">>', 1),
    ("Pregnancy ultrasound 2",
     '<<if _type is "harpy">>',
     '<<if _type is "harpy" or _type is "哈比">>', 2),
    ("Widgets Pub Fame",
     '<<if $pubfame.remy.password[2] is "the blood moon">>',
     '<<if $pubfame.remy.password[2] is "the blood moon" or $pubfame.remy.password[2] is "之下">>', 1),
    # 汉化包 i18n.json 把正文里的人名 Nobody 错写成了 <<case "nobody">>（switch 之外的子标签）
    # → 战后采集体液样本时必出红字「child tag <<case>> was found outside of a call to its parent macro <<switch>>」
    ("Widgets End Combat",
     '<<if isGwylanAbsent() is "nobody">><<case "nobody">><<else>>格威岚<</if>>',
     '<<if isGwylanAbsent() is "nobody">>无人<<else>>格威岚<</if>>', 1),
]

miss = []
total = 0
for pname, old, new, want in FIXES:
    sp = span(pname)
    if not sp:
        miss.append((pname, "找不到 passage"))
        continue
    s, e = sp
    body = data[s:e]
    oe, ne = H.escape(old, quote=False), H.escape(new, quote=False)
    c = body.count(oe)
    if c != want:
        miss.append((pname, "命中 %d 应 %d: %s" % (c, want, old)))
        continue
    data = data[:s] + body.replace(oe, ne) + data[e:]
    total += c

anchor = H.escape('<<widget "fishingMinigameStartText">>', quote=False)
if anchor in data:
    data = data.replace(anchor, H.escape("<!-- [AI01] 汉化值兼容的逻辑判断（社区 issue #579/#583 + 同类） -->", quote=False) + anchor, 1)
else:
    miss.append(("标记", "找不到 fishingMinigameStartText"))

if miss:
    for x in miss:
        print("[AI01] MISS", x)
    print("[AI01] FAIL（未写盘）")
    sys.exit(1)
open(HTML, "wb").write(data.encode("utf-8"))
print("[AI01] 修 %d 处  OK" % total)
