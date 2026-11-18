import html, json, re, zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
I18N = r"E:\TAML\_dol\work\i18n_dict.json"
OUT = r"E:\TAML\_dol\work\i18n_varstatic_safe.json"

z = zipfile.ZipFile(APK)
raw = z.read("assets/www/index.html")
g = html.unescape(raw.decode("utf-8", "replace"))
m = re.search(r'<tw-passagedata[^>]*name="Widgets variablesStatic"[^>]*>(.*?)</tw-passagedata>', g, re.S)
body = m.group(1)

d = json.load(open(I18N, "r", encoding="utf-8"))
items = [x for x in d["typeB"]["TypeBInputStoryScript"] if x.get("pN") == "Widgets variablesStatic"]

# 明确禁止：把「取值表」译成中文
FORBIDDEN = re.compile(r'<<set setup\.(breastsizes|penisSizes|bodyShapes|bodyShapescn|faceVariantOptions|faceStyleOptions)\s+to\s+\[')

fails = []
for it in items:
    f = it.get("f")
    if not f:
        continue
    pos = it.get("pos", -1)
    L = len(f)
    if any(0 <= pos + dd <= len(body) and body[pos + dd:pos + dd + L] == f for dd in (0, -1, -2, 1, 2)):
        continue
    start, end = max(0, pos - 10), min(len(body), pos + L + 30)
    if f in body[start:end]:
        continue
    fails.append(it)

CJK = re.compile(r"[\u4e00-\u9fff]")
safe, skipped = [], []

for it in fails:
    f, t = it.get("f"), it.get("t")
    if not f or t is None:
        continue
    if body.count(f) != 1:
        skipped.append(("f不唯一", f))
        continue
    # 1) 取值表译成中文 -> 禁止
    if FORBIDDEN.search(f):
        skipped.append(("取值表禁译", f))
        continue
    # 2) JSON 值被改成中文，且该键不是展示性文本
    vals_f = re.findall(r'":\s*"([^"]*)"', f)
    vals_t = re.findall(r'":\s*"([^"]*)"', t)
    keys = re.findall(r'"([A-Za-z_]+)"\s*:', f)
    corrupt = False
    for i, vf in enumerate(vals_f):
        if i >= len(vals_t):
            continue
        vt = vals_t[i]
        if CJK.search(vf) or not CJK.search(vt):
            continue
        # 值从英文变中文：只有展示性键才算安全
        if i < len(keys) and keys[i] in ("message", "description", "label", "text", "name", "title"):
            continue
        corrupt = True
        break
    if corrupt:
        skipped.append(("值被改写", f))
        continue
    safe.append((f, t))

print(f"失败条目 {len(fails)}  安全 {len(safe)}  跳过 {len(skipped)}")
print("\n跳过明细:")
for reason, f in skipped:
    print(f"  [{reason}] {f[:95]!r}")

json.dump(safe, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n写出: {OUT}  ({len(safe)} 条)")
