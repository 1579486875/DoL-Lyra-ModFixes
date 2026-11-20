"""F48：给 BODYPARTS_CN_NAME 内联完整部位表（幂等）。"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[F48] ❌ index 形态异常")
    sys.exit(1)

PARTS = {
    "left hand": "左手", "right hand": "右手", "hand": "手", "hands": "双手",
    "left arm": "左臂", "right arm": "右臂", "arm": "手臂", "arms": "双臂",
    "left leg": "左腿", "right leg": "右腿", "leg": "腿", "legs": "双腿",
    "foot": "脚", "feet": "双脚", "mouth": "嘴", "tongue": "舌头",
    "penis": "肉棒", "vagina": "阴部", "anus": "肛门", "ass": "屁股",
    "breasts": "胸部", "breast": "胸部", "nipple": "乳头", "nipples": "乳头",
    "buttocks": "臀部", "bottom": "臀部", "thigh": "大腿", "thighs": "大腿",
    "tail": "尾巴", "wings": "翅膀", "horn": "角", "horns": "角",
    "ears": "耳朵", "ear": "耳朵", "tentacle": "触手", "tentacles": "触手",
    "head": "头", "neck": "脖子", "chest": "胸口", "tummy": "肚子",
    "face": "脸", "lips": "嘴唇", "eyes": "眼睛", "eye": "眼睛",
    "fingers": "手指", "finger": "手指", "toes": "脚趾", "toe": "脚趾",
    "belly": "肚子", "navel": "肚脐", "waist": "腰", "hips": "胯部",
    "shoulders": "肩膀", "shoulder": "肩膀", "back": "背", "spine": "脊椎",
    "clitoris": "阴蒂", "clit": "阴蒂", "balls": "睾丸", "testicles": "睾丸",
    "pussy": "小穴", "cock": "肉棒", "dick": "肉棒", "cunt": "小穴",
    "teeth": "牙齿", "knee": "膝盖", "knees": "膝盖",
}
PJ = "{" + ",".join('"%s":"%s"' % (k, v) for k, v in PARTS.items()) + "}"
NEW = (
    'st.BODYPARTS_CN_NAME = function (x) {\n'
    '        var __PB = ' + PJ + ';\n'
    '        if (!x || typeof x !== "string") return x;\n'
    '        var k = String(x).toLowerCase().trim();\n'
    '        if (Object.prototype.hasOwnProperty.call(__PB, k)) return __PB[k];\n'
    '        try { return look(PART, x); } catch (e) { return x; }\n'
    '    };'
)

g = H.unescape(data)
n = 0
# 找所有 function(x){ return look(PART,x); } 形式
PAT = re.compile(r'st\.BODYPARTS_CN_NAME\s*=\s*function\s*\(\s*x\s*\)\s*\{\s*return\s+look\(PART,\s*x\);\s*\};')
for old in set(PAT.findall(data)):
    for a, b in ((H.escape(old, quote=False), H.escape(NEW, quote=False)), (old, NEW)):
        if a in data:
            c = data.count(a)
            data = data.replace(a, b)
            n += c
            break

if n:
    open(HTML, "wb").write(data.encode("utf-8"))

g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
has_penis = '"penis":"肉棒"' in g2
print(f"[F48] 替换 {n} 处  penis在表里={has_penis}  passage={len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")
sys.exit(0 if has_penis else 1)
