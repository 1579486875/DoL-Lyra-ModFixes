"""第 22-30 轮：以 vanilla 为基线做全量差异审计。

原则：modded 相对 vanilla 的每一处差异都必须是「有意的」（翻译/补丁），
任何非预期的结构差异就是 bug。
"""
import html
import re
import zipfile
from collections import Counter

VANILLA = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"
MODDED = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"


def load(apk):
    z = zipfile.ZipFile(apk)
    raw = z.read("assets/www/index.html")
    txt = raw.decode("utf-8", "replace")
    blocks = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', txt, re.S):
        blocks[html.unescape(m.group(1))] = html.unescape(m.group(2))
    return blocks, txt


vb, vt = load(VANILLA)
mb, mt = load(MODDED)

print("=" * 94)
print("第 22 轮：passage 集合差异")
print("=" * 94)
print(f"  vanilla: {len(vb)}   modded: {len(mb)}")
print(f"  vanilla 独有: {len(set(vb) - set(mb))}")
print(f"  modded  独有: {len(set(mb) - set(vb))}")

print("\n" + "=" * 94)
print("第 23 轮：宏配对（两边对比）")
print("=" * 94)


def strip_ns(s):
    for pat in (r"/\*.*?\*/", r"/%.*?%/", r"<!--.*?-->"):
        s = re.sub(pat, " ", s, flags=re.S)
    return s


PAIRS = [("if", r"<<if\b", "<</if>>"), ("for", r"<<for\b", "<</for>>"),
         ("switch", r"<<switch\b", "<</switch>>"), ("link", r"<<link\b", "<</link>>")]
for tag, op, cp in PAIRS:
    vo = sum(len(re.findall(op, strip_ns(b))) for b in vb.values())
    vc = sum(strip_ns(b).count(cp) for b in vb.values())
    mo = sum(len(re.findall(op, strip_ns(b))) for b in mb.values())
    mc = sum(strip_ns(b).count(cp) for b in mb.values())
    print(f"  {tag:<8} vanilla {vo:>6}/{vc:<6} modded {mo:>6}/{mc:<6}  {'✅' if mo == mc else '❌ 差 ' + str(mo - mc)}")

print("\n" + "=" * 94)
print("第 24 轮：widget 定义数量对比")
print("=" * 94)
vw = set(re.findall(r'<<widget\s+"([^"]+)"', "\n".join(vb.values())))
mw = set(re.findall(r'<<widget\s+"([^"]+)"', "\n".join(mb.values())))
print(f"  vanilla {len(vw)}   modded {len(mw)}")
print(f"  modded 丢失: {sorted(vw - mw)[:10]}")
print(f"  modded 新增: {sorted(mw - vw)[:10]}")

print("\n" + "=" * 94)
print("第 25 轮：CSS 类名总量（防止翻译污染 class）")
print("=" * 94)
for name, blocks in (("vanilla", vb), ("modded", mb)):
    allc = Counter()
    for b in blocks.values():
        allc.update(re.findall(r'class="([^"]{1,80})"', b))
    cjk_classes = [k for k in allc if re.search(r"[\u4e00-\u9fff]", k)]
    print(f"  {name}: class 种类 {len(allc)}，含中文的 {len(cjk_classes)}")
    for k in cjk_classes[:5]:
        print(f"      {k!r}")

print("\n" + "=" * 94)
print("第 26 轮：图片路径含中文")
print("=" * 94)
for name, blocks in (("vanilla", vb), ("modded", mb)):
    allg = []
    for b in blocks.values():
        allg.extend(re.findall(r'img/[A-Za-z0-9_/.\-]+\.(?:png|gif|jpg|webp)', b))
    cjk = [p for p in allg if re.search(r"[\u4e00-\u9fff]", p)]
    print(f"  {name}: 图片引用 {len(allg)}，含中文 {len(cjk)}")

print("\n" + "=" * 94)
print("第 27 轮：<<set>> 数量对比（防止语句被吞）")
print("=" * 94)
vs = sum(len(re.findall(r"<<set\b", b)) for b in vb.values())
ms = sum(len(re.findall(r"<<set\b", b)) for b in mb.values())
print(f"  vanilla {vs}   modded {ms}   差 {ms - vs}")
vr = sum(len(re.findall(r"<<run\b", b)) for b in vb.values())
mr = sum(len(re.findall(r"<<run\b", b)) for b in mb.values())
print(f"  <<run>>  vanilla {vr}   modded {mr}   差 {mr - vr}")

print("\n" + "=" * 94)
print("第 28 轮：<<if>> 里的字符串比较值（含中文的）")
print("=" * 94)


def cn_compare(blocks):
    out = Counter()
    for b in blocks.values():
        for m in re.finditer(r'<<(?:if|elseif)\s+\$[\w.\[\]]+\s+is(?:not)?\s+"([^"]{1,30})"', b):
            if re.search(r"[\u4e00-\u9fff]", m.group(1)):
                out[m.group(1)] += 1
    return out


vc2 = cn_compare(vb)
mc2 = cn_compare(mb)
print(f"  vanilla 含中文比较值: {len(vc2)} 种 / {sum(vc2.values())} 处")
print(f"  modded  含中文比较值: {len(mc2)} 种 / {sum(mc2.values())} 处")
new_cn = {k: v for k, v in mc2.items() if k not in vc2}
print(f"  modded 独有（我引入的）: {len(new_cn)}")
for k, v in new_cn.items():
    print(f"    {v:>3}  {k!r}")

print("\n" + "=" * 94)
print("第 29 轮：文件体积 / 结构")
print("=" * 94)
import os
for name, path in (("vanilla", VANILLA), ("modded", MODDED)):
    z = zipfile.ZipFile(path)
    n = len(z.namelist())
    idx = z.getinfo("assets/www/index.html")
    print(f"  {name}: APK {os.path.getsize(path):,} 字节，条目 {n}，index {idx.file_size:,} 字节")

print("\n" + "=" * 94)
print("第 30 轮：最终结论")
print("=" * 94)
print(f"  passage 集合一致: {set(vb) == set(mb)}")
print(f"  widget 集合一致: {vw == mw}")
