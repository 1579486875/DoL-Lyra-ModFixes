"""Q07：修 relation-box 里 NPC_CN_NAME 的宏嵌套错误（幂等）。"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[Q07] index 形态异常")
    sys.exit(1)

CMP = "_npcData.nam"
# 第12轮修正：
#  1) 显示处恢复汉化包原本的宏形态 <<NPC_CN_NAME _npcData.nam>>（宏在正文里是合法的，只是不能进 <<if>>）。
#     maplebirch 框架的 zone 补丁正是按 /\t_npcData.nam|\t<<NPC_CN_NAME _npcData.nam>>/ 匹配后换成
#     maplebirch.auto(...)；旧版改成 <<print setup.NPC_CN_NAME(...)>> 导致该补丁 unmatched（运行时日志实测）。
#  2) <<npcrelationship>> 的参数必须是英文原名：它内部用 V.NPCName.findIndex(i => i.nam === _args[0]) 查人，
#     旧版传中文名 → 每个 NPC 的关系描述都报「<<npcrelationship>>提供了错误的参数」。恢复 vanilla 写法。
SHOW = "<<NPC_CN_NAME _npcData.nam>>"

FIXES = [
    ('<<if (<<NPC_CN_NAME _npcData.nam>>>>>> is ("Ivory Wraith") or ($wraith.mimic is <<NPC_CN_NAME _npcData.nam>>>>>> and $wraith.revealed))>>',
     '<<if (_npcData.nam is "Ivory Wraith") or ($wraith.mimic is _npcData.nam and $wraith.revealed)>>'),
    ('<<if <<NPC_CN_NAME _npcData.nam>>>>>> is ("Ivory Wraith") and',
     '<<if _npcData.nam is "Ivory Wraith" and'),
    ('<<elseif $wraithIntro and $wraith.mimic is <<NPC_CN_NAME _npcData.nam>>>>>> and',
     '<<elseif $wraithIntro and $wraith.mimic is _npcData.nam and'),
    ('<<npcrelationship <<NPC_CN_NAME _npcData.nam>>>>>>>>',
     '<<npcrelationship _npcData.nam>>'),
    ('<<NPC_CN_NAME _npcData.nam>>>>>>>>？', SHOW + '？'),
    ('<<NPC_CN_NAME _npcData.nam>>>>>>', SHOW),
]

total = 0
for old, new in FIXES:
    hit = 0
    for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            hit += c
            break
    total += hit

if total:
    open(HTML, "wb").write(data.encode("utf-8"))

# 校验：relation-box 的 <<if>> 里不能有 <
g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
m = re.search(r'<<widget "relation-box">>(.*?)<</widget>>', g, re.S)
bad = 0
if m:
    for mm in re.finditer(r"<<if\b(.*?)>>", m.group(1)):
        body = mm.group(1)
        s = re.sub(r'"[^"]*"', lambda x: " " * len(x.group(0)), body)
        s = re.sub(r"'[^']*'", lambda x: " " * len(x.group(0)), s)
        s = re.sub(r"`[^`]*`", lambda x: " " * len(x.group(0)), s)
        if "<" in s:
            bad += 1

print("[Q07] 修 %d 处  passage=%d  relation-box if含< = %d  %s" % (
    total, len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML, 'rb').read().decode('utf-8', 'replace'))),
    bad, "OK" if bad == 0 else "FAIL"))
sys.exit(0 if bad == 0 else 1)
