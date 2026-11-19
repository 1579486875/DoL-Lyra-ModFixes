"""查 Widgets Wraith 里 widget 配对 + _speechWraith 那段是否破坏了语法。"""
import html
import re
import zipfile

MOD = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def get(path, name):
    z = zipfile.ZipFile(path)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        if html.unescape(m.group(1)) == name:
            return html.unescape(m.group(2))
    return ""


NAME = "Widgets Wraith"
for label, path in (("vanilla", VAN), ("modded", MOD)):
    b = get(path, NAME)
    o = len(re.findall(r"<<widget\b", b))
    c = b.count("<</widget>>")
    print(f"{label}: 长度 {len(b)}, <<widget>> {o}/{c}  {'✅' if o == c else '❌ 差 ' + str(o-c)}")

print("\n" + "=" * 94)
print("modded 里 _speechWraith 附近的原始文本")
print("=" * 94)
b = get(MOD, NAME)
i = b.find("_speechWraith")
# 找第二次出现（第一处是赋值）
cnt = 0
pos = 0
while True:
    j = b.find("_speechWraith", pos)
    if j < 0:
        break
    cnt += 1
    if cnt <= 3:
        print(f"\n[{cnt}] @{j}: {b[max(0,j-350):j+250]!r}")
    pos = j + 1

print("\n" + "=" * 94)
print("vanilla 对应位置")
print("=" * 94)
vb = get(VAN, NAME)
k = 0
pos = 0
while True:
    j = vb.find("_speechWraith", pos)
    if j < 0:
        break
    k += 1
    if k <= 3:
        print(f"\n[{k}] @{j}: {vb[max(0,j-350):j+250]!r}")
    pos = j + 1
