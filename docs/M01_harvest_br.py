"""M01：彻底查 Harvest Street 的 <<br>> 来源。"""
import html as H
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
g = H.unescape(zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace"))

PASSAGES = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', g, re.S):
    PASSAGES[m.group(1)] = m.group(2)

body = PASSAGES.get("Harvest Street", "")
print(f"Harvest Street 长度: {len(body)}")

print("\n" + "=" * 95)
print("1. 所有 <<br 形式")
print("=" * 95)
for pat, label in ((r"<<br\s*>>", "<<br>>"), (r"<<\s*br\b", "<<br"),
                   (r"&lt;&lt;br", "&lt;&lt;br"), (r"<br>", "<br>"),
                   (r'"<<\s*"\s*\+', '"<< " +')):
    hs = list(re.finditer(pat, body))
    print(f"  {label}: {len(hs)}")

print("\n" + "=" * 95)
print("2. 所有 <<...>> 宏名（看有没有异常）")
print("=" * 95)
names = {}
for m in re.finditer(r"<<\s*/?\s*([A-Za-z_][A-Za-z0-9_\-]*)", body):
    n = m.group(1).lower()
    names[n] = names.get(n, 0) + 1
for n, c in sorted(names.items(), key=lambda x: -x[1]):
    print(f"  {c:>3} <<{n}>>")

print("\n" + "=" * 95)
print("3. 找 wiki() / wikifier() / print 里含 <br> 的")
print("=" * 95)
for m in re.finditer(r"(?:\$\.wiki|wikifier|sWikifier|wikifyEval|<<print|<<=)[^;\n]{0,150}<br>", body):
    print(f"  @{m.start()}: {m.group(0)[:250]!r}")

print("\n" + "=" * 95)
print("4. 找 'br' 作为变量/字符串")
print("=" * 95)
for m in list(re.finditer(r'"br"|\'br\'', body))[:10]:
    print(f"  @{m.start()}: {body[max(0,m.start()-150):m.start()+150]!r}")

print("\n" + "=" * 95)
print("5. 完整 passage 前 3000 字（找可疑拼接）")
print("=" * 95)
print(body[:3000])
