"""Y02：扫转义残留 —— 三重转义 / 单重转义在正文里 / 异常实体。

index 的正确形态是「标签明文 + 正文 HTML 转义」，所以：
  - passage body 里  &lt;&lt;if  → 正常（SugarCube 会 unescape 后解析）
  - 但如果出现      &amp;lt;&lt;  → 双重转义（已修）
  - 如果出现        &amp;amp;lt; → 三重转义（新问题）
  - 如果出现        &amp;quot;  → 双重转义的引号

另外检查：正文里有没有「应该解析成 < 但没解析」的 &lt;（前面没有 &lt 配对）
"""
import html as H
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
raw = zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace")

print("=" * 95)
print("1. 各级转义总量")
print("=" * 95)
levels = [
    ("&lt;", "单重（正常，正文）"),
    ("&amp;lt;", "双重（已修）"),
    ("&amp;amp;lt;", "三重 ★"),
    ("&amp;amp;amp;lt;", "四重 ★★"),
    ("&gt;", "单重 gt"),
    ("&amp;gt;", "双重 gt"),
    ("&amp;amp;gt;", "三重 gt ★"),
    ("&quot;", "单重 quot"),
    ("&amp;quot;", "双重 quot"),
    ("&amp;amp;quot;", "三重 quot ★"),
    ("&#39;", "单重 apos"),
    ("&amp;#39;", "双重 apos"),
    ("&amp;amp;", "双重 amp"),
    ("&amp;amp;amp;", "三重 amp ★"),
]
for k, label in levels:
    n = raw.count(k)
    flag = " ⚠️" if "★" in label and n > 0 else ""
    print(f"  {n:>7}  {k:<18} {label}{flag}")

print("\n" + "=" * 95)
print("2. 三重转义明细")
print("=" * 95)
for pat in (r"&amp;amp;lt;", r"&amp;amp;gt;", r"&amp;amp;quot;", r"&amp;amp;amp;"):
    ms = list(re.finditer(pat, raw))
    if ms:
        print(f"\n  [{pat}]  {len(ms)} 处")
        for m in ms[:6]:
            print(f"    @{m.start()}: {raw[max(0,m.start()-90):m.start()+140]!r}")
    else:
        print(f"\n  [{pat}]  0 处 ✅")

print("\n" + "=" * 95)
print("3. passage 标签被转义的情况（应为 0）")
print("=" * 95)
n_esc_tag = len(re.findall(r"&lt;tw-passagedata", raw))
print(f"  &lt;tw-passagedata: {n_esc_tag} 处 {'✅' if n_esc_tag == 0 else '❌'}")
n_esc_close = len(re.findall(r"&lt;/tw-passagedata", raw))
print(f"  &lt;/tw-passagedata: {n_esc_close} 处 {'✅' if n_esc_close == 0 else '❌'}")

print("\n" + "=" * 95)
print("4. 正文里的 &quot; / &#39; 异常（在 passage body 内、非 JS 上下文）")
print("=" * 95)
g = H.unescape(raw)
P = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', g, re.S):
    P[m.group(1)] = m.group(2)

n4 = 0
samples4 = []
for pname, body in P.items():
    b = re.sub(r"<<script>>.*?<</script>>", "", body, flags=re.S)
    for m in re.finditer(r"&quot;|&#39;", b):
        # 前后有中文
        ctx = b[max(0, m.start() - 40):m.start() + 50]
        if not re.search(r"[\u4e00-\u9fff]", ctx):
            continue
        n4 += 1
        if len(samples4) < 12:
            samples4.append((pname, ctx))
print(f"  共 {n4} 处")
for p, c in samples4:
    print(f"    [{p}] {c!r}")

print("\n" + "=" * 95)
print("汇总")
print("=" * 95)
bad = 0
for k, label in levels:
    if "★" in label and raw.count(k) > 0:
        bad += raw.count(k)
print(f"  三重及以上转义: {bad}")
print(f"  标签被转义: {n_esc_tag + n_esc_close}")
print(f"  正文异常实体: {n4}")
