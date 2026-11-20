"""M02：静态分析 —— 哪些 widget 会输出 <br> 给 Wikifier 当宏解析。

<<br>> 报错的机制：某个 widget 用 <<print>> 或 <<= 输出了一段 HTML，
其中含 <br>，而这段内容又被 Wikifier 二次解析（wiki()/wikifier()/<<display>>），
SugarCube 会把 <<...>> 当宏，但如果内容是 "<br>" 则不会被当宏。

真正会产生 "<<br>>" 的是：字符串拼接时把 < 写成 << 或者 Wikifier 把 <br> 转成 <<br>>。

重点查：Harvest Street 里调用的 widget 中，哪些真的输出了 <br>/<<br>>。
"""
import html as H
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
g = H.unescape(zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace"))

PASSAGES = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', g, re.S):
    PASSAGES[m.group(1)] = m.group(2)

# Harvest Street 调用的 widget
CALLED = ["effects", "gettarget", "streeteffects", "exhibitionism", "orgasmstreet",
          "passoutstreet", "group", "person1", "person", "eventsstreet", "icon",
          "brothelicon", "pubicon", "busstationicon", "add_link", "hidedisplay",
          "displaylinks", "map", "generaterole", "factoryicon", "roadicon",
          "mer", "elk", "buswait", "loiter", "industrial", "stormdrain"]

print("=" * 95)
print("1. 每个 widget 里有没有 <<br>> 或 wiki 二次解析")
print("=" * 95)
for w in CALLED:
    body = None
    for pname, pbody in PASSAGES.items():
        m = re.search(r'<<widget "' + re.escape(w) + r'">>(.*?)<</widget>>', pbody, re.S)
        if m:
            body = m.group(1)
            break
    if body is None:
        print(f"  [<<{w}>>] ❌ widget 不存在")
        continue
    flags = []
    if re.search(r"<<br\s*>>", body):
        flags.append("<<br>>")
    if re.search(r"&lt;&lt;br", body):
        flags.append("&lt;&lt;br")
    if re.search(r"wiki|wikifier|wikifyEval|<<display", body):
        flags.append("二次解析")
    if re.search(r'"<"\s*\+|"<"\s*\+\s*"br"', body):
        flags.append('"<"+')
    print(f"  [<<{w}>>] 长度{len(body):>6}  {flags if flags else 'OK'}")

print("\n" + "=" * 95)
print("2. 全局找 <<print>> 输出含 <br>> 且有 wiki 二次解析的")
print("=" * 95)
for m in re.finditer(r"(?:\.wiki|wikifier|sWikifier|wikifyEval)\s*\([^;]{0,400}<br>", g):
    print(f"  @{m.start()}: {m.group(0)[:300]!r}")

print("\n" + "=" * 95)
print("3. 全局找 '<<br' 与 'br' 拼接")
print("=" * 95)
for pat in (r'["\']<<br', r'`<<br', r'"<<"\s*\+\s*"br"', r'"<"\s*\+\s*"<"\s*\+\s*"br"'):
    hs = list(re.finditer(pat, g))
    if hs:
        print(f"  {pat!r}: {len(hs)}")
        for h in hs[:3]:
            print(f"    {g[max(0,h.start()-150):h.start()+150]!r}")

print("\n" + "=" * 95)
print("4. add_link / displaylinks 的实现")
print("=" * 95)
for w in ("add_link", "displaylinks"):
    for pname, pbody in PASSAGES.items():
        m = re.search(r'<<widget "' + re.escape(w) + r'">>(.*?)<</widget>>', pbody, re.S)
        if m:
            print(f"\n  [<<{w}>>]")
            print(f"  {m.group(1)[:800]!r}")
            break
