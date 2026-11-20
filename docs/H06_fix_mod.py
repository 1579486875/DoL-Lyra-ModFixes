"""H06（幂等）：补全 Npc Name CN 模组的 BODYPARTS 表。

该模组在 forceSetup() 里无条件覆盖 setup.BODYPARTS_CN_NAME，
但自己的 BODYPARTS 表只有 30 个键，缺性器官等。
改它自己的表 = 最彻底的解法。
"""
import base64
import html as H
import io
import json
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")

if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("❌ index 形态异常")
    sys.exit(1)

g = H.unescape(data)
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", g, re.S)
if not m:
    print("❌ 无 modDataValueZipList")
    sys.exit(1)

block_start, block_end = m.start(1), m.end(1)
block = m.group(1)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', block)
print(f"模组 zip {len(parts)}")

# 需要补的部位（Npc Name CN 缺的）
EXTRA_PARTS = {
    "penis": "肉棒", "vagina": "阴部", "anus": "肛门", "ass": "屁股",
    "breasts": "胸部", "breast": "胸部", "nipple": "乳头", "nipples": "乳头",
    "buttocks": "臀部", "bottom": "臀部", "tongue": "舌头", "lips": "嘴唇",
    "tail": "尾巴", "tails": "尾巴", "wings": "翅膀", "wings2": "翅膀",
    "horns": "角", "ears": "耳朵", "tentacle": "触手", "tentacles": "触手",
    "tummy": "肚子", "waist": "腰", "hips": "胯部", "spine": "脊椎",
    "clitoris": "阴蒂", "clit": "阴蒂", "ball": "睾丸", "balls": "睾丸",
    "testicles": "睾丸", "pussy": "小穴", "cock": "肉棒", "dick": "肉棒",
    "cunt": "小穴", "teeth": "牙齿", "knees": "膝盖", "thighs": "大腿",
    "legs": "腿", "arms": "手臂", "hands": "手", "feet": "脚",
    "shoulders": "肩膀", "fingers": "手指", "finger": "手指",
    "toes": "脚趾", "toe": "脚趾", "eyes": "眼睛", "navel": "肚脐",
    "belly": "肚子", "back": "背部", "face": "脸",
}

# 额外别名（mod 用的是驼峰，如 leftArm）
ALIAS = {
    "leftArm": "左臂", "rightArm": "右臂", "leftLeg": "左腿", "rightLeg": "右腿",
    "leftFoot": "左脚", "rightFoot": "右脚", "leftHand": "左手", "rightHand": "右手",
}

fixed = 0
new_block = block

for s in parts:
    raw = base64.b64decode(re.sub(r"\s+", "", s))
    if raw[:2] != b"PK":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(raw))
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
        if bj.get("name") != "Npc Name CN":
            continue
    except Exception:
        continue

    print("\n✅ 找到 Npc Name CN")

    buf = io.BytesIO()
    changed = []
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
        for info in zz.infolist():
            d = zz.read(info.filename)
            if info.filename.endswith(".js"):
                try:
                    txt = d.decode("utf-8")
                except Exception:
                    txt = None
                if txt and "var BODYPARTS = {" in txt:
                    # 找 BODYPARTS 表，补全
                    mm = re.search(r"var BODYPARTS = \{([^}]*)\};", txt, re.S)
                    if mm:
                        body = mm.group(1)
                        existing = set(re.findall(r'"([^"]+)"\s*:', body))
                        allneed = dict(EXTRA_PARTS)
                        allneed.update(ALIAS)
                        add = []
                        for k, v in allneed.items():
                            if k not in existing:
                                add.append('"%s": "%s"' % (k, v))
                        if add:
                            # 在最后一个条目后插入
                            nb = body.rstrip()
                            if not nb.rstrip().endswith(","):
                                nb = nb.rstrip() + ","
                            # 保持缩进
                            indent = "\n\t\t"
                            nb = nb + indent + ", ".join(add) + "\n\t"
                            new_txt = txt.replace(mm.group(0), "var BODYPARTS = {%s};" % nb)
                            d = new_txt.encode("utf-8")
                            changed.append((info.filename, len(add)))
                    # 同时给 partCN 加兜底（如果 tr 返回原值，说明表里没有）
                elif txt and "function partCN" in txt and "BODYPARTS_CN_NAME" in txt:
                    changed.append((info.filename, 0))
            zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            zi.compress_type = info.compress_type
            zi.external_attr = info.external_attr
            zo.writestr(zi, d)

    if any(c[1] > 0 for c in changed):
        nb64 = base64.b64encode(buf.getvalue()).decode("ascii")
        pat = re.compile(r'"' + re.escape(s[:80]) + r'[A-Za-z0-9+/=\s]*"')
        new_block = pat.sub(lambda _: '"' + nb64 + '"', new_block, count=1)
        fixed += 1
        for f, n in changed:
            if n:
                print(f"   ✅ {f}: 补 {n} 个部位")
    else:
        print(f"   ⚠️ 未改动: {changed}")

if fixed:
    data = data[:block_start] + new_block + data[block_end:]
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"\n✅ 已写入 index")

# 校验：重新解模组看表
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", g2, re.S)
print("\n" + "=" * 90)
print("校验")
print("=" * 90)
for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m2.group(1)):
    raw = base64.b64decode(re.sub(r"\s+", "", s))
    if raw[:2] != b"PK":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(raw))
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
        if bj.get("name") != "Npc Name CN":
            continue
        js = zz.read("npcNameCN.js").decode("utf-8")
        mm = re.search(r"var BODYPARTS = \{([^}]*)\};", js, re.S)
        body = mm.group(1)
        keys = set(re.findall(r'"([^"]+)"\s*:', body))
        print(f"  BODYPARTS 键数: {len(keys)}")
        for kw in ("penis", "vagina", "anus", "breasts", "tongue", "buttocks", "wings"):
            print(f"    {'OK ' if kw in keys else 'MISS'} {kw}")
    except Exception:
        continue

print(f"\npassage: {len(re.findall(r'<tw-passagedata[^>]*name=', open(HTML,'rb').read().decode('utf-8','replace')))}")
