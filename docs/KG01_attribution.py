"""第 31-35 轮：风险项归属（vanilla 对照）+ 收尾。"""
import html
import re
import zipfile
from collections import Counter

VANILLA = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"
MODDED = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"


def load(apk):
    z = zipfile.ZipFile(apk)
    txt = z.read("assets/www/index.html").decode("utf-8", "replace")
    blocks = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', txt, re.S):
        blocks[html.unescape(m.group(1))] = html.unescape(m.group(2))
    return blocks


vb = load(VANILLA)
mb = load(MODDED)


def metrics(blocks):
    g = "\n".join(blocks.values())
    return {
        "length_assert": len(re.findall(r"<<(?:if|elseif)\s+[^\n>]*?(?:setup\.\w+|\$\w+)\s*\.length", g)),
        "direct_out": len(re.findall(r"<<=\s*[\w.]+\s*>>", g)),
        "div": len(re.findall(r"Math\.(?:round|floor|ceil)\s*\([^)]*/\s*[A-Za-z_$]", g)),
        "json_parse": len(re.findall(r"JSON\.parse\s*\(", g)),
        "optional_chain": len(re.findall(r"\?\.[A-Za-z_]", g)),
        "arr_prop": len(re.findall(r"\$\w+\[[^\]]{1,40}\]\.\w+", g)),
    }


vm = metrics(vb)
mm = metrics(mb)

print("=" * 94)
print("第 31 轮：风险项 vanilla vs modded")
print("=" * 94)
print(f"  {'指标':<20}{'vanilla':>10}{'modded':>10}{'差':>8}")
for k in vm:
    print(f"  {k:<20}{vm[k]:>10}{mm[k]:>10}{mm[k] - vm[k]:>8}")

print("\n" + "=" * 94)
print("第 32 轮：结构完整性复验")
print("=" * 94)
print(f"  passage: vanilla {len(vb)}  modded {len(mb)}  {'✅' if set(vb) == set(mb) else '❌'}")
vw = set(re.findall(r'<<widget\s+"([^"]+)"', "\n".join(vb.values())))
mw = set(re.findall(r'<<widget\s+"([^"]+)"', "\n".join(mb.values())))
print(f"  widget : vanilla {len(vw)}  modded {len(mw)}  {'✅' if vw == mw else '❌'}")

print("\n" + "=" * 94)
print("第 33 轮：宏配对全量复验")
print("=" * 94)
PAIRS = [("if", r"<<if\b", "<</if>>"), ("for", r"<<for\b", "<</for>>"),
         ("switch", r"<<switch\b", "<</switch>>"), ("link", r"<<link\b", "<</link>>"),
         ("button", r"<<button\b", "<</button>>"), ("capture", r"<<capture\b", "<</capture>>"),
         ("widget", r"<<widget\b", "<</widget>>")]
ok_all = True
for tag, op, cp in PAIRS:
    mo = sum(len(re.findall(op, b)) for b in mb.values())
    mc = sum(b.count(cp) for b in mb.values())
    ok = mo == mc
    ok_all &= ok
    print(f"  {tag:<10} {mo:>6}/{mc:<6}  {'✅' if ok else '❌ 差 ' + str(mo - mc)}")
print(f"\n  全部平衡: {ok_all}")

print("\n" + "=" * 94)
print("第 34 轮：本轮修复项复核")
print("=" * 94)
g = "\n".join(mb.values())
checks = {
    "fringetypeCN 兜底": "$fringetypeCN ||" in g,
    "hairtypeCN 兜底": "$hairtypeCN ||" in g,
    "compoundWraith 已修": "compoundWraith" not in g,
    "worn.handheld 已修": not re.search(r"<<if\s+worn\.handheld", g),
    "settings.watersportsEnabled 已修": not re.search(r"(?<![\w$.])settings\.watersportsEnabled", g),
    "5 张映射表": all(("setup." + t + " to") in g for t in
                 ["NPCTypeList_cn_name", "NPCNameList_cn_name", "NPCTitleList_cn_name",
                  "majorAreas_cn_name", "CafeFoodList_cn_name"]),
    "_faceVariantscn 动态": "_faceVariantscn = Object.keys" in g,
    "cheats-npcs 兜底": "setup.NPCNameList ||" in g,
    "widget 名无中文": len([n for n in mw if re.search(r"[\u4e00-\u9fff]", n)]) == 0,
}
for k2, v in checks.items():
    print(f"  {'✅' if v else '❌'} {k2}")

print("\n" + "=" * 94)
print("第 35 轮：英文残留最终确认")
print("=" * 94)
CJK = re.compile(r"[\u4e00-\u9fff]")


def strip_all(s):
    s = html.unescape(s)
    for _ in range(3):
        s = re.sub(r"/\*.*?\*/", " ", s, flags=re.S)
        s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    for marker in ("/*", "<!--"):
        i = s.find(marker)
        if 0 <= i < len(s) * 0.6:
            s = s[:i]
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    lines = [ln for ln in s.split("\n") if not re.search(r"<<[a-zA-Z]", ln)]
    s = " ".join(lines)
    s = re.sub(r"<[^>]{1,400}>", " ", s)
    s = re.sub(r"\[\[[^\]]*\]\]", " ", s)
    return re.sub(r"\s+", " ", s)


SENT = re.compile(r"[A-Z][^.!?]{18,400}[.!?]")
BAD = re.compile(r"(?:\$|_\w|\bisnot\b|\binstanceof\b|\btypeof\b|\bnull\b|\bundefined\b|"
                 r"\bto\s+\$|\bgt\b|\bgte\b|\blt\b|\blte\b|\bis\s+\$|=>|===|!==)")
FUNC = re.compile(r"\b(?:the|a|an|and|or|but|you|your|is|are|was|were|to|of|in|"
                  r"it|that|this|with|for|his|her|he|she|they|them|their)\b", re.I)
SYSTEM = {"PassageFooter", "gameStartOnly", "StoryInit", "StoryCaption", "StoryTitle",
          "StoryMenu", "StorySubtitle", "StoryAuthor", "StoryBanner", "StoryData",
          "StoryJavaScript", "StoryStylesheet", "StoryDisplayTitle", "Debug"}

cnt = 0
samples = []
for pn, b in mb.items():
    if pn in SYSTEM or pn.startswith("Widgets "):
        continue
    txt = strip_all(b)
    for m2 in SENT.finditer(txt):
        seg = m2.group(0).strip()
        if CJK.search(seg) or BAD.search(seg):
            continue
        if len(re.findall(r"[A-Za-z']+", seg)) < 6:
            continue
        if len(FUNC.findall(seg)) < 3:
            continue
        if not re.match(r"^[A-Z][a-z]", seg):
            continue
        cnt += 1
        if len(samples) < 5:
            samples.append((pn, seg[:120]))
print(f"  残留英文剧情句: {cnt}")
for pn, s in samples:
    print(f"    [{pn}] {s!r}")
