# -*- coding: utf-8 -*-
"""第4轮：扫所有模组 Twee 文案里「面向玩家的英文残留」。

判据：
- 一段连续英文（>=3 个单词）
- 不在 << >> 宏里、不在 HTML 属性里、不在注释里
- 不是专有名词列表（如 NPC 名、颜色名）
"""
import base64
import io
import json
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")
mz = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", h, re.S)

# 白名单：专有名词 / 常见英文短语（不是漏翻）
WHITE = re.compile(
    r"\b(SugarCube|ModLoader|JavaScript|HTML|CSS|JSON|API|UI|NPC|PC|HP|XP|URL|ID|OK|"
    r"MapleBirch|BESC|BEEESSS|DoL|APK|Android|Windows|Chrome|Edge|"
    r"SmartPhone|PhotoPack|CombatSkills|BasicNeeds|DoLSims|DomRobin|LocationsExt|"
    r"TweeReplacer|ReplacePatcher|ImageLoaderHook|ModdedClothesAddon|"
    r"deadwood|reblooms|Cattery|FertilityExpansion|HonestMarkets|GuideToMe|"
    r"true|false|null|undefined|NaN|Infinity|console|log|warn|error)\b",
    re.I,
)

# 中文标点 / 汉字存在则说明是中文句子，跳过
HAS_CJK = re.compile(r"[\u4e00-\u9fff]")

found = []
for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', mz.group(1)):
    try:
        d = base64.b64decode(re.sub(r"\s+", "", s))
    except Exception:
        continue
    if d[:2] != b"PK":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(d))
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
    except Exception:
        continue
    nm = bj.get("name") or "?"
    for f in zz.namelist():
        if not f.lower().endswith((".twee", ".tw")):
            continue
        try:
            if zz.getinfo(f).file_size > 3_000_000:
                continue
            t = zz.read(f).decode("utf-8", "replace")
        except Exception:
            continue
        # 去掉宏、HTML 标签、注释
        clean = re.sub(r"<<.*?>>", " ", t, flags=re.S)
        clean = re.sub(r"<[^>]+>", " ", clean)
        clean = re.sub(r"/\*.*?\*/", " ", clean, flags=re.S)
        clean = re.sub(r"//[^\n]*", " ", clean)
        # 找连续英文
        for mm in re.finditer(r"[A-Za-z][A-Za-z'’,\.\!\?\-\s]{24,}", clean):
            seg = mm.group(0).strip()
            if HAS_CJK.search(seg):
                continue
            # 至少 4 个单词
            words = [w for w in re.split(r"\s+", seg) if re.fullmatch(r"[A-Za-z][A-Za-z'’\-]*", w)]
            if len(words) < 4:
                continue
            # 全是白名单词
            rest = WHITE.sub(" ", seg)
            rest_words = [w for w in re.split(r"\s+", rest) if re.fullmatch(r"[A-Za-z][A-Za-z'’\-]*", w)]
            if len(rest_words) < 4:
                continue
            found.append((nm, f.split("/")[-1], seg[:140]))

# 去重
seen = set()
out = []
for x in found:
    k = (x[0], x[2][:60])
    if k in seen:
        continue
    seen.add(k)
    out.append(x)

print("=== 疑似英文残留: %d 处 ===" % len(out))
by_mod = {}
for nm, f, seg in out:
    by_mod.setdefault(nm, []).append((f, seg))

for nm in sorted(by_mod, key=lambda x: -len(by_mod[x])):
    items = by_mod[nm]
    print("\n【%s】%d 处" % (nm, len(items)))
    for f, seg in items[:5]:
        print("   %-24s %s" % (f, seg.replace("\n", " ")[:110]))
