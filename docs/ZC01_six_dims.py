"""第 17-30 轮：剩余 6 个维度的综合深挖。

A) modded 独有的链接目标（确认上一轮）
B) widget 参数个数与调用不匹配
C) 变量消失（vanilla 有赋值、modded 完全没有）
D) CSS class / id 含中文
E) <<switch>> 的 case 重复
F) <<script>> 里误用 $var（SugarCube 里 script 内不能直接用 $var）
"""
import html
import re
import zipfile
from collections import Counter, defaultdict

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"
CJK = re.compile(r"[\u4e00-\u9fff]")


def load(p):
    z = zipfile.ZipFile(p)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    blocks = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        out = {}
        b = html.unescape(m.group(2))
        blocks[html.unescape(m.group(1))] = b
    return html.unescape(raw), blocks


mg, mb = load(APK)
vg, vb = load(VAN)


def targets_of(raw):
    out = set()
    for m in re.finditer(r'<<link\s+\[\[(.{1,300}?)\]\]', raw, re.S):
        inner = m.group(1)
        if "|" in inner:
            t = inner.rsplit("|", 1)[1].strip()
        elif "->" in inner:
            t = inner.rsplit("->", 1)[1].strip()
        else:
            t = inner.strip()
        for x in (t, t.strip("'\"")):
            out.add(x)
    for m in re.finditer(r'<<(?:goto|display|include)\s+"([^"]+)"', raw):
        out.add(m.group(1))
    return out


# ---------- A) modded 独有缺失链接 ----------
print("=" * 90)
print("A) modded 独有的缺失链接目标")
print("=" * 90)
mt, vt = targets_of(mg), targets_of(vg)


def missing(ts, blocks):
    return {t for t in ts
            if t and not any(c in t for c in "$_+[]()<<")
            and t.strip("'\"") not in blocks}


mm, vm = missing(mt, mb), missing(vt, vb)
only = mm - vm
print(f"  modded 独有: {len(only)}")
for x in sorted(only)[:15]:
    print(f"    {x!r}")

# ---------- B) widget 参数匹配 ----------
print("\n" + "=" * 90)
print("B) widget 参数个数 vs 调用")
print("=" * 90)
# 定义：<<widget "name">> 里用 _args[N]
wdefs = {}
for m in re.finditer(r'<<widget\s+"([^"]+)"\s*>>(.*?)<</widget>>', mg, re.S):
    name, body = m.group(1), m.group(2)
    idxs = [int(x) for x in re.findall(r"_args\[(\d+)\]", body)]
    wdefs[name] = max(idxs) + 1 if idxs else 0
print(f"  widget 定义 {len(wdefs)} 个，其中带参数的 {sum(1 for v in wdefs.values() if v)} 个")

mismatch = []
for name, need in wdefs.items():
    if not need:
        continue
    # 调用时传了几个参数
    for cm in re.finditer(r"<<" + re.escape(name) + r"((?:\s+[^>]{1,80})?)>>", mg):
        argstr = cm.group(1).strip()
        cnt = len(re.findall(r"(?:\"[^\"]*\"|'[^']*'|[^\s]+)", argstr)) if argstr else 0
        if cnt < need and argstr and not any(x in argstr for x in ("$", "_", "(")):
            mismatch.append((name, need, cnt, argstr[:60]))
uniq = sorted(set(mismatch))[:15]
print(f"  参数不足: {len(set(mismatch))} 种")
for n, need, got, a in uniq:
    print(f"    {n}(需要 {need}, 传 {got}): {a!r}")

# ---------- C) 变量消失 ----------
print("\n" + "=" * 90)
print("C) 变量消失（vanilla 有赋值，modded 完全没有）")
print("=" * 90)


def assigned(raw):
    s = set(re.findall(r"\$(\w+)\s*(?:to|=|\+=|-=)\s", raw))
    s |= set(re.findall(r"<<unset\s+\$(\w+)", raw))
    s |= set(re.findall(r"<<set\s+\$(\w+)", raw))
    return s


ma, va = assigned(mg), assigned(vg)
lost = sorted(va - ma)
print(f"  vanilla 有、modded 无: {len(lost)}")
for x in lost[:20]:
    print(f"    ${x}")
    for m in list(re.finditer(r"\$" + re.escape(x) + r"\b", vg))[:1]:
        print(f"      vanilla: {vg[max(0,m.start()-100):m.start()+100]!r}")

# ---------- D) CSS class/id 含中文 ----------
print("\n" + "=" * 90)
print("D) CSS class / id 含中文")
print("=" * 90)
hits = []
for m in re.finditer(r'class="([^"]{0,200})"', mg):
    if CJK.search(m.group(1)):
        hits.append(("class", m.group(1)[:60]))
for m in re.finditer(r'id="([^"]{0,120})"', mg):
    if CJK.search(m.group(1)):
        hits.append(("id", m.group(1)[:60]))
c = Counter(hits)
if c:
    print(f"  {len(c)} 种")
    for (k, v), n in c.most_common(15):
        print(f"    {k}={v!r} × {n}")
else:
    print("  ✅ 0 种")

# ---------- E) switch case 重复 ----------
print("\n" + "=" * 90)
print("E) <<switch>> 的 case 重复")
print("=" * 90)
dup = []
for m in re.finditer(r"<<switch[^>]*>>(.*?)<</switch>>", mg, re.S):
    body = m.group(1)
    cases = re.findall(r'<<case\s+"?([^">]+)"?>>', body)
    cnt = Counter(cases)
    d = [k for k, v in cnt.items() if v > 1]
    if d:
        dup.append(d)
print(f"  重复 case: {len(dup)} 组")
for d in dup[:10]:
    print(f"    {d}")

# ---------- F) script 里误用 $var ----------
print("\n" + "=" * 90)
print("F) <<script>> 里直接用 $var（SugarCube 不允许）")
print("=" * 90)
bad = []
for m in re.finditer(r"<<script>>(.*?)<</script>>", mg, re.S):
    src = m.group(1)
    # $var 出现在 script 里（排除字符串内）
    s2 = re.sub(r'"(?:[^"\\]|\\.)*"', '""', src)
    s2 = re.sub(r"'(?:[^'\\]|\\.)*'", "''", s2)
    s2 = re.sub(r"`(?:[^`\\]|\\.)*`", "``", s2)
    if re.search(r"\$\w+", s2):
        bad.append(s2[:100])
print(f"  {len(bad)} 处")
for b in bad[:8]:
    print(f"    {b!r}")
