"""最终全量验证：结构 / 宏 / 我的注入 / 与 vanilla 差异。"""
import html
import re
import zipfile
from collections import Counter

MODDED = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VANILLA = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(apk):
    z = zipfile.ZipFile(apk)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    out = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        out[html.unescape(m.group(1))] = html.unescape(m.group(2))
    return out, raw


mb, mraw = load(MODDED)
vb, vraw = load(VANILLA)
g = "\n".join(mb.values())

print("=" * 94)
print("1) 结构")
print("=" * 94)
print(f"  passage: vanilla {len(vb)}  modded {len(mb)}  {'✅' if set(vb) == set(mb) else '❌'}")
vw = set(re.findall(r'<<widget\s+"([^"]+)"', "\n".join(vb.values())))
mw = set(re.findall(r'<<widget\s+"([^"]+)"', g))
print(f"  widget : vanilla {len(vw)}  modded {len(mw)}  新增 {sorted(mw - vw)}")

print("\n" + "=" * 94)
print("2) 宏配对")
print("=" * 94)
PAIRS = [("if", r"<<if\b", "<</if>>"), ("for", r"<<for\b", "<</for>>"),
         ("switch", r"<<switch\b", "<</switch>>"), ("link", r"<<link\b", "<</link>>"),
         ("button", r"<<button\b", "<</button>>"), ("capture", r"<<capture\b", "<</capture>>"),
         ("widget", r"<<widget\b", "<</widget>>"), ("script", r"<<script>>", "<</script>>")]
allok = True
for tag, op, cp in PAIRS:
    mo = sum(len(re.findall(op, b)) for b in mb.values())
    mc = sum(b.count(cp) for b in mb.values())
    ok = mo == mc
    allok &= ok
    print(f"  {tag:<10} {mo:>6}/{mc:<6}  {'✅' if ok else '❌ 差 ' + str(mo - mc)}")

print("\n" + "=" * 94)
print("3) 宏内部语法（配对扫描）")
print("=" * 94)


def scan_bad(blocks, pattern):
    bad = []
    for pn, b in blocks.items():
        for m in re.finditer(pattern, b):
            i = m.end()
            depth = 1
            while i < len(b) and depth > 0:
                if b.startswith("<<", i):
                    depth += 1
                    i += 2
                elif b.startswith(">>", i):
                    depth -= 1
                    i += 2
                else:
                    i += 1
            expr = b[m.end():i - 2]
            e = re.sub(r'"[^"]*"', '""', expr)
            e = re.sub(r"'[^']*'", "''", e)
            e = re.sub(r"`[^`]*`", "``", e)
            if "<<" in e:
                bad.append((pn, expr[:100]))
    return bad


for label, pat in (("if", r"<<(if|elseif|unless|while)\b"),
                   ("set/run/print", r"<<(set|run|print|=)\b")):
    bb = scan_bad(mb, pat)
    vv = scan_bad(vb, pat)
    new = {x[0] for x in bb} - {x[0] for x in vv}
    print(f"  {label:<16} modded {len(bb)}  vanilla {len(vv)}  modded独有 {len(new)}")
    for x in sorted(new)[:5]:
        print(f"      {x}")

print("\n" + "=" * 94)
print("4) 我注入的宏检查")
print("=" * 94)
for kw in ("NPC_CN_NAME", "NPC_CN_TYPE", "BODYPARTS_CN_NAME"):
    m = re.search(r'<<widget\s+"' + kw + r'"\s*>>(.*?)<</widget>>', g, re.S)
    if m:
        body = m.group(1).strip()
        good = body.startswith("<<=") and body.endswith(">>")
        print(f"  {kw:<20} {'✅' if good else '⚠️'}  {body[:90]!r}")
    else:
        print(f"  {kw:<20} ❌ 未找到")

# setup 函数
m = re.search(r"st\.NPC_CN_TYPE\s*=\s*function", g)
print(f"  setup.NPC_CN_TYPE 赋值: {'✅' if m else '❌'}")

print("\n" + "=" * 94)
print("5) 关键数据表")
print("=" * 94)
for t in ("NPCTypeList_cn_name", "NPCNameList_cn_name", "NPCTitleList_cn_name",
          "majorAreas_cn_name", "CafeFoodList_cn_name"):
    print(f"  setup.{t:<24} {'✅' if ('setup.' + t + ' to') in g else '❌'}")

print("\n" + "=" * 94)
print("6) 结论")
print("=" * 94)
print(f"  宏配对全平衡: {allok}")
print(f"  passage 一致: {set(vb) == set(mb)}")
