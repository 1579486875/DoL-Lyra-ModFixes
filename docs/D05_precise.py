"""D05：精确验证「且」+ 查 Harvest Street 的 <<br>> 来源。"""
import html as H
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
raw = zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace")
g = H.unescape(raw)

print("=" * 90)
print("1) 精确查 <<if>> 里的「且」（单行内）")
print("=" * 90)
for line_no, line in enumerate(g.split("\n"), 1):
    if "且" not in line:
        continue
    if "<<if" in line or "<<elseif" in line:
        # 只看 <<if ...>> 内部
        for m in re.finditer(r"<<if\b([^<>]*)>>", line):
            if "且" in m.group(1):
                print(f"  L{line_no}: {m.group(0)!r}")

print("\n" + "=" * 90)
print("2) Harvest Street passage")
print("=" * 90)
m = re.search(r'<tw-passagedata[^>]*name="Harvest Street"[^>]*>(.*?)</tw-passagedata>',
              raw, re.S)
if m:
    body = H.unescape(m.group(1))
    print(f"  长度 {len(body)}")
    # 找 br 相关
    for pat_str in (r"<<br", r"<br>", r"\\n"):
        hs = list(re.finditer(pat_str, body))
        print(f"  {pat_str!r}: {len(hs)}")
        for mm in hs[:5]:
            print(f"    {body[max(0,mm.start()-120):mm.start()+120]!r}")
else:
    print("  ⚠️ 未找到 passage")

print("\n" + "=" * 90)
print("3) 全局找 'br' 被当宏调用的地方")
print("=" * 90)
PATTERNS = [
    (r'<<\s*br\s*>>', "<<br>>"),
    (r'<<\s*br\s*/\s*>>', "<<br/>>"),
    (r'"\s*<<\s*"\s*\+\s*"?br', '"<< "+ "br'),
    (r'wikifier\s*\(\s*["\']<<br', 'wikifier("<<br'),
]
for p, label in PATTERNS:
    hs = list(re.finditer(p, g))
    print(f"  {label}: {len(hs)}")
    for mm in hs[:3]:
        print(f"    {g[max(0,mm.start()-100):mm.start()+100]!r}")

print("\n" + "=" * 90)
print("4) 找 '<br>' 在 JS 字符串里不带转义的情况（会被 Wikifier 当宏）")
print("=" * 90)
# 找 sWikifier('<br>') / wikifyEval("<br>") 之类
for mm in list(re.finditer(r'(sWikifier|wikifyEval|wikifier|<<=)\s*\(\s*["\'][^"\']*<br>', g))[:10]:
    print(f"  {g[max(0,mm.start()-80):mm.start()+200]!r}\n")

print("=" * 90)
print("5) 检查是否存在 <<br>> 会被拼出来的路径")
print("=" * 90)
# 找 content: "<<" + xxx + ">>" 这类动态宏
for mm in list(re.finditer(r'content:\s*"<<"\s*\+\s*(\w+)', g))[:10]:
    print(f"  {g[max(0,mm.start()-150):mm.start()+200]!r}\n")
