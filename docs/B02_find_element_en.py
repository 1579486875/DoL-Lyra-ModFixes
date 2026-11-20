"""B02：找 element("span", "英文") 这类 JS 硬编码英文提示，全量列出。"""
import html
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
g = html.unescape(zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace"))

print("=" * 100)
print("1) element(\"span\", \"...\") 里的纯英文")
print("=" * 100)

pat = re.compile(r'element\(\s*"span"\s*,\s*"([^"]{8,300})"')
hits = []
for m in pat.finditer(g):
    t = m.group(1)
    # 纯英文（无中文）
    if re.search(r"[\u4e00-\u9fff]", t):
        continue
    # 至少 3 个英文单词
    if len(re.findall(r"[A-Za-z]{2,}", t)) < 3:
        continue
    hits.append((m.start(), t))

print(f"  命中 {len(hits)} 条\n")
for pos, t in hits[:60]:
    print(f"  @{pos}: {t!r}")

print("\n" + "=" * 100)
print("2) 同样检查 element(其它标签, \"英文\")")
print("=" * 100)
pat2 = re.compile(r'element\(\s*"[a-z]+"\s*,\s*"([^"]{10,300})"\s*,\s*"[a-z]+"\s*\)')
hits2 = []
for m in pat2.finditer(g):
    t = m.group(1)
    if re.search(r"[\u4e00-\u9fff]", t):
        continue
    if len(re.findall(r"[A-Za-z]{2,}", t)) < 3:
        continue
    hits2.append((m.start(), t))

print(f"  命中 {len(hits2)} 条（可能和上面重叠）\n")

# 去重合并
allhits = {}
for pos, t in hits + hits2:
    allhits[t] = allhits.get(t, 0) + 1

print("=" * 100)
print(f"3) 去重后 {len(allhits)} 条不同的英文提示")
print("=" * 100)
for t, c in sorted(allhits.items(), key=lambda x: -x[1]):
    print(f"  {c:>2}× {t[:160]!r}")
