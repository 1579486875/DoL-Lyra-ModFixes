"""V08：对比基线的 /* */ 数量 + 验证 SugarCube 是否显示它们。"""
import html as H
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
GOOD = r"E:\TAML\_dol\archive\DoL-Lyra-0.5.12.13-CHS-modded_20261120-061313_修复arsc可安装.apk"

g = H.unescape(zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace"))
gb = H.unescape(zipfile.ZipFile(GOOD).read("assets/www/index.html").decode("utf-8", "replace"))


def count_in_passages(t):
    P = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', t, re.S):
        P[m.group(1)] = m.group(2)
    n = 0
    for pname, body in P.items():
        b = re.sub(r"<<script>>.*?<</script>>", "", body, flags=re.S)
        n += len(re.findall(r"/\*[^*\n]{0,180}?\*/", b))
    return n, len(P)


na, pa = count_in_passages(g)
nb, pb = count_in_passages(gb)
print("=" * 90)
print("passage 正文里的 /* */ 数量")
print("=" * 90)
print(f"  基线: {nb} 处 / {pb} passage")
print(f"  当前: {na} 处 / {pa} passage")
print(f"  差异: {na - nb:+d}")

print("\n" + "=" * 90)
print("如果数量一致 → 是原版设计，不动")
print("=" * 90)

# 验证 SugarCube 是否把 /* */ 当注释：
# 找 SugarCube 源码里的注释处理
print("\n" + "=" * 90)
print("查 SugarCube 的注释语法支持")
print("=" * 90)
for kw in ("/%", "<!--", "commentRegExp", "cleanupComments"):
    ms = list(re.finditer(re.escape(kw), g))
    print(f"  {kw!r}: {len(ms)} 处")

# 找 SugarCube 里处理注释的代码
for pat in (r"cleanupComments", r"comments\s*[:=]", r"/%[\s\S]{0,80}%/"):
    ms = list(re.finditer(pat, g))
    if ms:
        print(f"\n  匹配 {pat!r}: {len(ms)} 处")
        for m in ms[:2]:
            print(f"    {g[max(0,m.start()-150):m.start()+250]!r}")

# 检查那 1 处 _text_output "The "
print("\n" + "=" * 90)
print("_text_output \"The \" 的位置")
print("=" * 90)
for m in re.finditer(r'<<set\s+_text_output\s+to\s+"The\s*"', g):
    print(f"  @{m.start()}: {g[max(0,m.start()-400):m.start()+400]!r}")
