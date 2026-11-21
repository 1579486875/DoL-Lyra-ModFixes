"""F12：中文文本里的英文残留修复（幂等）。"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r"<tw-passagedata[^>]*name=", data)) < 16000:
    print("[F12] ❌ index 形态异常，拒绝修改")
    sys.exit(1)

FIXES = [
    # 回车键
    ("选择你的操作，然后单击继续或者按enter键继续。",
     "选择你的操作，然后单击继续或者按回车键继续。"),
    # Wink -> 媚眼
    ("悉尼接过了箱子，给了你一个Wink，随后就这样淡定地夹在了腋下。",
     "悉尼接过了箱子，朝你抛了个媚眼，随后就这样淡定地夹在了腋下。"),
    # 束缚 play
    ("“看来你喜欢束缚play？”", "“看来你喜欢束缚玩法？”"),
    # 第12轮：官方 JS 译文烘焙（AP01）后，衣物描述里也出现了「束缚play」（clothing-under-*.js 两处）
    ("为那些喜欢束缚play的人准备。", "为那些喜欢束缚玩法的人准备。"),
    # the 冠词（后面接 NPC 全名）
    ('你握紧吊坠盒，心中想着<<if ["Black Wolf", "Great Hawk"].includes($worn.neck.photo)>>the <</if>><<= $worn.neck.photo>>。',
     '你握紧吊坠盒，心中想着<<= setup.NPC_CN_NAME($worn.neck.photo)>>。'),
]

total = 0
for old, new in FIXES:
    hit = 0
    # 第12轮：两种形态都要替换（passage 正文是转义形态，JS 里是原样），不能命中一种就 break
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            hit += c
    if hit:
        total += hit
        print(f"  ✅ {hit}x {old[:50]!r}")

if total:
    open(HTML, "wb").write(data.encode("utf-8"))

# 校验
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
BAD = {
    "按enter键": g.count("按enter键"),
    "一个Wink": g.count("一个Wink"),
    "束缚play": g.count("束缚play"),
    "心中想着the": g.count("心中想着the"),
}
ok = all(v == 0 for v in BAD.values())
print(f"[F12] 修 {total} 处  passage={len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}  " +
      "  ".join(f"{k}={v}" for k, v in BAD.items()) + f"  {'OK' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
