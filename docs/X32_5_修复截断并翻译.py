# -*- coding: utf-8 -*-
"""修复 MapleBirchCE 两条被截断的函数式 text（上游 bug）+ 应用其余 8 条翻译。"""
import base64
import io
import json
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
PREFIX = "var VANILLA_TRAITS_RAW = "
DRY = "--write" not in sys.argv

# 两条截断的：整条替换（补全 + 翻译）
BROKEN = {
    "生发配方": (
        '() =&gt; {\n\t\t\t\t\t\treturn `A hair growth formula has been applied, to encourage faster hair growth. ${_pills["Hair Growth Formula"].doseTaken} day${_pills["Hair Growth Formula"].dose',
        '() =&gt; {\n\t\t\t\t\t\treturn `已使用生发配方，以促进头发更快生长。距今 ${_pills["Hair Growth Formula"].doseTaken} 天。`;\n\t\t\t\t\t}',
    ),
    "抗寄生虫乳膏": (
        '() =&gt; {\n\t\t\t\t\t\treturn `A parasite-repelling cream, preventing further internal parasite impregnation. ${_pills["Anti-Parasite Cream"].doseTaken} day${_pills["Anti-Parasite Cream"',
        '() =&gt; {\n\t\t\t\t\t\treturn `已使用抗寄生虫乳膏，可防止体内寄生虫进一步受孕。距今 ${_pills["Anti-Parasite Cream"].doseTaken} 天。`;\n\t\t\t\t\t}',
    ),
}

# 其余 8 条
FN_TRANS = {
    "斯德哥尔摩综合征：狼群": (
        '() =&gt; V.settings.bestialityEnabled ? "They\'re just cute animals." : "They\'re just cute monsters."',
        '() =&gt; V.settings.bestialityEnabled ? "它们只是可爱的小动物。" : "它们只是可爱的小怪物。"',
    ),
    "斯德哥尔摩综合征：巨鹰": (
        '() =&gt; V.greathawkmonster === 2 || !V.settings.bestialityEnabled ? "&lt;&lt;nnpc_He \'Great Hawk\'&gt;&gt; only wants a mate." : "It only wants a mate."',
        '() =&gt; V.greathawkmonster === 2 || !V.settings.bestialityEnabled ? "&lt;&lt;nnpc_He \'Great Hawk\'&gt;&gt;只想要一个伴侣。" : "它只想要一个伴侣。"',
    ),
    "接受：孕肚": (
        '() =&gt; playerAwareTheyArePregnant() ? "You\'re proud of your lifebearing belly." : "You\'re proud of your large belly."',
        '() =&gt; playerAwareTheyArePregnant() ? "你为自己能孕育生命的肚子而自豪。" : "你为自己的大肚子而自豪。"',
    ),
}

FRAGMENT_TRANS = [
    ('let result = `You have ${_pills["fertility booster"].doseTaken gte 2 ? "overdosed on pills" : "taken a pill"} that `;',
     'let result = `你${_pills["fertility booster"].doseTaken gte 2 ? "过量服用了" : "服用了"}一片药，`;'),
    ('let result = `You have ${_pills["contraceptive"].doseTaken gte 2 ? "overdosed on pills" : "taken a pill"} that `;',
     'let result = `你${_pills["contraceptive"].doseTaken gte 2 ? "过量服用了" : "服用了"}一片药，`;'),
    ('let result = `You have taken a pill that`;',
     'let result = `你服下了一片药，`;'),
    ('result += " prevents the re-sizing of your penis.";',
     'result += "它能阻止阴茎的尺寸变化。";'),
    ('let result = `You have ${_pills["penis growth"].doseTaken gte 2 ? "overdosed on" : "taken"} pills that `;',
     'let result = `你${_pills["penis growth"].doseTaken gte 2 ? "过量服用了" : "服用了"}药片，`;'),
    ('let result = `You have ${_pills["penis reduction"].doseTaken gte 2 ? "overdosed on" : "taken"} pills that `;',
     'let result = `你${_pills["penis reduction"].doseTaken gte 2 ? "过量服用了" : "服用了"}药片，`;'),
]

raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)

target = None
for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1)):
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
    if (bj.get("name") or "") == "MapleBirchCE":
        target = (s, zz, bj)
        break

if not target:
    print("❌ 未找到")
    sys.exit(1)

s_old, zz, bj = target
t = zz.read("javascript/maplebirchce.js").decode("utf-8", "replace")
i = t.find(PREFIX + "[")
j = t.find("\n];", i)
arr = json.loads(re.sub(r",\s*\]\s*$", "]", t[i + len(PREFIX):j + 2].rstrip()))
print("条目:", len(arr))

cnt_fix = 0
cnt_tr = 0
for item in arr:
    nm = item.get("name", "")
    tx = str(item.get("text", ""))
    if not tx.strip().startswith("("):
        continue

    if nm in BROKEN:
        old, new = BROKEN[nm]
        if tx == old:
            item["text"] = new
            cnt_fix += 1
            print("  🔧 修复+翻译:", nm)
        else:
            print("  ⚠ 不匹配:", nm, "| 实际", len(tx), "期望", len(old))
        continue

    if nm in FN_TRANS:
        old, new = FN_TRANS[nm]
        if tx == old:
            item["text"] = new
            cnt_tr += 1
            print("  ✅ 整段:", nm)
        continue

    tx2 = str(item.get("text", ""))
    changed = False
    for of, nf in FRAGMENT_TRANS:
        if of in tx2:
            tx2 = tx2.replace(of, nf)
            changed = True
    if changed:
        item["text"] = tx2
        cnt_tr += 1
        print("  ✅ 片段:", nm)

print("\n修复截断: %d | 翻译: %d" % (cnt_fix, cnt_tr))

if DRY:
    print("[dry-run]")
    sys.exit(0)

lines = [json.dumps(x, ensure_ascii=False, separators=(",", ":")) for x in arr]
new_arr = "[\n    " + ",\n  ".join(lines) + "\n]"
chk = json.loads(new_arr)
assert len(chk) == len(arr)
print("回读校验: %d 条 ✓" % len(chk))

t2 = t[:i + len(PREFIX)] + new_arr + t[j + 2:]
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zz.infolist():
        d = zz.read(info.filename)
        if info.filename == "javascript/maplebirchce.js":
            d = t2.encode("utf-8")
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, d)

new_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
raw2 = raw.replace(s_old, new_b64, 1)
npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
if npass2 != npass:
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
