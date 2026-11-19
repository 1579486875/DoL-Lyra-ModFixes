"""第 31-35 轮：收尾验证（JS 语法 / 存档变量 / 英文残留 / 性能 / 最终）。"""
import base64
import html
import io
import json
import os
import re
import subprocess
import tempfile
import zipfile
from collections import Counter

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
raw = z.read("assets/www/index.html")
g = html.unescape(raw.decode("utf-8", "replace"))

j = raw.find(b"[", raw.find(b"window.modDataValueZipList"))
k = raw.find(b"]", j)
parts = re.findall(r'"([A-Za-z0-9+/=\s]+)"', raw[j + 1:k].decode("utf-8", "replace"))

mods = []
for s in parts:
    b = base64.b64decode(re.sub(r"\s+", "", s))
    if b[:2] != b"PK":
        continue
    zz = zipfile.ZipFile(io.BytesIO(b))
    if "boot.json" not in zz.namelist():
        continue
    bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
    mods.append((bj.get("name") or "?", bj, zz))

print("=" * 94)
print("第 31 轮：JS 语法")
print("=" * 94)
tmp = os.path.join(tempfile.gettempdir(), "chk.js")
jsn = jse = 0
for name, bj, zz in mods:
    for f in bj.get("scriptFileList") or []:
        try:
            t = zz.read(f).decode("utf-8", "ignore")
        except Exception:
            continue
        jsn += 1
        open(tmp, "w", encoding="utf-8").write(t)
        r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if r.returncode != 0:
            jse += 1
            print(f"  ❌ [{name}] {f}")
print(f"  检查 {jsn} 个 JS，语法错误 {jse}  {'✅' if jse == 0 else '❌'}")

print("\n" + "=" * 94)
print("第 32 轮：存档变量完整性（关键变量是否都有兜底或初始化）")
print("=" * 94)
KEY = ["$player", "$NPCList", "$worn", "$settings", "$version", "$phase",
       "$location", "$time", "$rng", "$statFreeze", "$temple_wall_victim"]
for v in KEY:
    defs = len(re.findall(r"<<set\s+" + re.escape(v) + r"\s+(?:to|\+=|=[^=])", g))
    refs = len(re.findall(re.escape(v) + r"\b", g))
    print(f"  {v:<24} 定义 {defs:>4}  引用 {refs:>5}  {'✅' if defs or refs < 3 else '⚠️'}")

print("\n" + "=" * 94)
print("第 33 轮：英文残留（严格判据）")
print("=" * 94)
CJK = re.compile(r"[\u4e00-\u9fff]")
def strip_all(s):
    s = html.unescape(s)
    for _ in range(3):
        s = re.sub(r"/\*.*?\*/", " ", s, flags=re.S)
        s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    for marker in ("/*", "<!--"):
        i = s.find(marker)
        if i >= 0:
            s = s[:i] if i < len(s) // 2 else s
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    lines = [ln for ln in s.split("\n") if not re.search(r"<<[a-zA-Z]", ln)]
    s = " ".join(lines)
    s = re.sub(r"<[^>]{1,400}>", " ", s)
    s = re.sub(r"\[\[[^\]]*\]\]", " ", s)
    return re.sub(r"\s+", " ", s)

SENT = re.compile(r"[A-Z][^.!?]{25,300}[.!?]")
cnt = 0
samples = []
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw.decode("utf-8", "replace"), re.S):
    pn = html.unescape(m.group(1))
    txt = strip_all(m.group(2))
    for mm in SENT.finditer(txt):
        seg = mm.group(0).strip()
        if CJK.search(seg):
            continue
        if len(re.findall(r"[A-Za-z']+", seg)) < 5:
            continue
        if re.search(r"\b(?:function|return|var|let|const|typeof|undefined|null)\b", seg):
            continue
        cnt += 1
        if len(samples) < 8:
            samples.append((pn, seg[:110]))
print(f"  严格判据下的英文句子: {cnt}")
for pn, s in samples:
    print(f"    [{pn}] {s!r}")

print("\n" + "=" * 94)
print("第 34 轮：性能")
print("=" * 94)
infos = [(i.filename, i.file_size) for i in z.infolist() if i.file_size > 0]
print(f"  解压总量: {sum(s for _, s in infos)/1048576:.1f} MB，文件 {len(infos)}")
print(f"  index: {len(raw)/1048576:.2f} MB")
print(f"  APK  : {os.path.getsize(APK)/1048576:.2f} MB")

print("\n" + "=" * 94)
print("第 35 轮：本轮修复项复核")
print("=" * 94)
checks = {
    "$compoundWraith 已修": "compoundWraith" not in g or g.count("compoundWraith") <= 1,
    "if worn.handheld 已修": not re.search(r"<<if\s+worn\.handheld", g),
    "settings.watersportsEnabled 已修": not re.search(r"(?<![\w$.])settings\.watersportsEnabled", g),
    "5 张映射表": all(("setup." + t + " to") in g for t in
                 ["NPCTypeList_cn_name", "NPCNameList_cn_name", "NPCTitleList_cn_name",
                  "majorAreas_cn_name", "CafeFoodList_cn_name"]),
    "bodyShapescn": "setup.bodyShapescn to" in g,
    "_faceVariantscn 动态": "_faceVariantscn = Object.keys" in g,
    "faceVariantOptions 6 键": len(re.findall(r'"[^"]+"\s*:', re.search(r"<<set setup\.faceVariantOptions to \{.*?\}\s*>>", g, re.S).group(0))) == 7,
    "cheats-npcs 兜底": "setup.NPCNameList ||" in g,
    "widget 名无中文": len([n for n in re.findall(r'<<widget\s+"([^"]+)"', g) if CJK.search(n)]) == 0,
    "宏配对 link": len(re.findall(r"<<link\b", g)) == g.count("<</link>>"),
}
for k2, v in checks.items():
    print(f"  {'✅' if v else '❌'} {k2}")
