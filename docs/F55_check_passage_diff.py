"""F55（第42轮）：查 passage 少了哪个。"""
import re
import zipfile
from collections import Counter

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
ARCHIVE = r"E:\TAML\_dol\archive"
GOOD = ARCHIVE + r"\DoL-Lyra-0.5.12.13-CHS-modded_20261120-061313_修复arsc可安装.apk"

cur = zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace")
base = zipfile.ZipFile(GOOD).read("assets/www/index.html").decode("utf-8", "replace")


def pnames(t):
    # 只匹配不带转义的（排除 JS 字符串里的 pid=\"...\"）
    return re.findall(r'<tw-passagedata\s+(?![^>]*\\")[^>]*name="([^"]*)"', t)


cn = pnames(cur)
bn = pnames(base)
print(f"基线 {len(bn)} / 当前 {len(cn)}")

sc, sb = set(cn), set(bn)
print(f"\n缺失: {sorted(sb - sc)}")
print(f"多出: {sorted(sc - sb)}")

# 重复检查
print(f"\n当前重复: {dict((k, v) for k, v in Counter(cn).items() if v > 1)}")

# 宽匹配（含转义）
cn2 = re.findall(r'<tw-passagedata[^>]*name="([^"]*)"', cur)
bn2 = re.findall(r'<tw-passagedata[^>]*name="([^"]*)"', base)
print(f"\n宽匹配: 基线 {len(bn2)} / 当前 {len(cn2)}")
print(f"宽匹配缺失: {sorted(set(bn2) - set(cn2))}")
print(f"宽匹配多出: {sorted(set(cn2) - set(bn2))}")
