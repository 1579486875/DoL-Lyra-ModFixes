"""第 1-8 轮：HTML 标签配对检查（div/span/table/label/b/i/u/em/strong）。

翻译替换可能删掉或破坏标签，导致布局崩坏、点击区域错位。
只检查配对数量，不检查嵌套顺序（顺序问题噪声太大）。
"""
import html
import re
import zipfile
from collections import Counter, defaultdict

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"

TAGS = ["div", "span", "table", "tr", "td", "label", "b", "i", "u", "em",
        "strong", "small", "p", "br", "hr", "ul", "li", "ol", "a"]


def load(p):
    z = zipfile.ZipFile(p)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    out = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        out[html.unescape(m.group(1))] = html.unescape(m.group(2))
    return out


mb = load(APK)
vb = load(VAN)
print(f"passage: modded {len(mb)} / vanilla {len(vb)}")


def tag_counts(text):
    """统计每个标签的开/闭数量（排除 <script> 和 <style> 内容）。"""
    t = re.sub(r"<script\b.*?</script>", " ", text, flags=re.S | re.I)
    t = re.sub(r"<style\b.*?</style>", " ", t, flags=re.S | re.I)
    c = Counter()
    for tag in TAGS:
        if tag in ("br", "hr"):
            c[tag] = len(re.findall(r"<" + tag + r"\b[^>]*>", t, re.I))
            continue
        o = len(re.findall(r"<" + tag + r"\b[^>]*>", t, re.I))
        cl = len(re.findall(r"</" + tag + r"\s*>", t, re.I))
        c[tag] = o - cl
    return c


def audit(blocks, label):
    print("\n" + "=" * 90)
    print(f"[{label}] 标签不配对的 passage")
    print("=" * 90)
    bad = defaultdict(list)
    for pn, b in blocks.items():
        c = tag_counts(b)
        for tag, diff in c.items():
            if diff != 0:
                bad[tag].append((pn, diff))
    total = 0
    for tag in TAGS:
        lst = bad.get(tag, [])
        if not lst:
            continue
        total += len(lst)
        print(f"\n  <{tag}> 不配对 {len(lst)} 个 passage")
        for pn, d in lst[:6]:
            print(f"    {pn}: {'+' if d > 0 else ''}{d}")
    if not total:
        print("  ✅ 全部配对")
    return bad


m_bad = audit(mb, "modded")
v_bad = audit(vb, "vanilla")

print("\n" + "=" * 90)
print("modded 独有不配对（才是我们引入的）")
print("=" * 90)
only = 0
for tag in TAGS:
    ms = {pn for pn, _ in m_bad.get(tag, [])}
    vs = {pn for pn, _ in v_bad.get(tag, [])}
    d = ms - vs
    if d:
        only += len(d)
        print(f"\n  <{tag}> modded 独有 {len(d)} 个:")
        for pn in sorted(d)[:10]:
            diff = dict(m_bad[tag])[pn]
            print(f"    {pn}: {'+' if diff > 0 else ''}{diff}")
            # 显示上下文
            b = mb.get(pn, "")
            print(f"      预览: {b[:180]!r}")
if not only:
    print("  ✅ 无 modded 独有")
print(f"\n合计 modded 独有: {only}")
