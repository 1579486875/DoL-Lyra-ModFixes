"""定位那个吞掉 3.5MB 的 <<script>> 块。"""
import html
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(p):
    z = zipfile.ZipFile(p)
    return html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


mg = load(APK)
vg = load(VAN)

for label, g in (("modded", mg), ("vanilla", vg)):
    o = len(re.findall(r"<<script>>", g))
    c = g.count("<</script>>")
    print(f"{label}: <<script>> {o} / <</script>> {c}  {'✅' if o == c else '❌ 差 ' + str(o-c)}")

print("\n" + "=" * 88)
print("modded 里所有 <<script>> 块的长度")
print("=" * 88)
blocks = []
for m in re.finditer(r"<<script>>(.*?)<</script>>", mg, re.S):
    blocks.append((len(m.group(1)), m.start(), m.group(1)))
blocks.sort(reverse=True)
for n, pos, src in blocks[:6]:
    print(f"\n  @{pos}  长度 {n:,}")
    print(f"    前 200: {src[:200]!r}")

print("\n" + "=" * 88)
print("定位第一个超大块：它前面的原文")
print("=" * 88)
big_n, big_pos, big_src = blocks[0]
print(f"  块 @{big_pos}，长度 {big_n:,}")
print(f"  块前面 500 字符: {mg[max(0,big_pos-500):big_pos]!r}")

print("\n" + "=" * 88)
print("vanilla 里同样位置")
print("=" * 88)
# 找 vanilla 里 "but preprocesses the contents" 的位置
key = "but preprocesses the contents"
i = vg.find(key)
print(f"  vanilla '{key}' @{i}")
if i > 0:
    print(f"  前面 600: {vg[max(0,i-600):i]!r}")

j = mg.find(key)
print(f"\n  modded  '{key}' @{j}")
if j > 0:
    print(f"  前面 600: {mg[max(0,j-600):j]!r}")
