import html, re, zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
g = html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))

m = re.search(r'<tw-passagedata[^>]*name="Widgets Settings"[^>]*>(.*?)</tw-passagedata>', g, re.S)
body = m.group(1)
print("Widgets Settings 长度:", len(body))

print("\n=== <<=  ...>> 中含 Object. 的 ===")
seen = set()
for mm in re.finditer(r"<<=[^>]{0,500}?>>", body):
    expr = mm.group(0)
    if "Object." in expr:
        key = expr[:120]
        if key in seen:
            continue
        seen.add(key)
        print(f"\n  {expr[:300]!r}")

print("\n=== 所有 Object.xxx( 调用 ===")
cnt = 0
for mm in re.finditer(r"Object\.([A-Za-z]+)\s*\(", body):
    cnt += 1
    if cnt <= 20:
        print(f"  @{mm.start()} Object.{mm.group(1)}: {body[max(0,mm.start()-80):mm.start()+140]!r}")
print(f"\n合计 {cnt} 处")
