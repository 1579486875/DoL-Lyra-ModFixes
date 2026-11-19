"""定位 <<if>> 不平衡的 passage。"""
import html
import re

for label, path in (
    ("当前 index", r"E:\TAML\_dol\work\index_modded6.html"),
    ("旧 APK", None),
):
    if path:
        raw = open(path, "rb").read().decode("utf-8", "replace")
    else:
        import zipfile
        z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
        raw = z.read("assets/www/index.html").decode("utf-8", "replace")

    print("=" * 94)
    print(label)
    print("=" * 94)
    total_o = total_c = 0
    bad = []
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        pn = html.unescape(m.group(1))
        body = html.unescape(m.group(2))
        # 去注释
        b = re.sub(r"/\*.*?\*/", " ", body, flags=re.S)
        b = re.sub(r"<!--.*?-->", " ", b, flags=re.S)
        b = re.sub(r"/%.*?%/", " ", b, flags=re.S)
        o = len(re.findall(r"<<if\b", b))
        c = b.count("<</if>>")
        total_o += o
        total_c += c
        if o != c:
            bad.append((pn, o, c))
    print(f"  总计 {total_o}/{total_c}  差 {total_o - total_c}")
    print(f"  不平衡 passage: {len(bad)}")
    for pn, o, c in bad[:15]:
        print(f"    [{pn}] {o}/{c}")
    print()
