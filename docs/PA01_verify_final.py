"""紧急验证：最终 APK 里这些英文是否真的还是英文。"""
import html
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
g = html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))

TARGETS = ["Pain", "Arousal", "Fatigue", "Stress", "Trauma", "Control", "Allure",
           "Condoms", "Genitals", "Makeup", "Body", "Head", "Personality"]

print("=" * 94)
print("最终 APK 里的实际内容")
print("=" * 94)
for t in TARGETS:
    # 找 UI 形态：>Pain< 或 "Pain" 或 <<numberStepper "Pain"
    n1 = len(re.findall(r">\s*" + t + r"\s*[<:]", g))
    n2 = len(re.findall(r'<<"' + t + r'"', g))
    n3 = len(re.findall(r"'" + t + r"'", g))
    print(f"  {t:<12} >X<:{n1:>4}  <<\"X\":{n2:>3}  'X':{n3:>4}")

print("\n" + "=" * 94)
print("Pain / Arousal 的实际上下文")
print("=" * 94)
for kw in ("Pain", "Arousal", "Condoms", "Genitals", "Makeup"):
    print(f"\n--- {kw} ---")
    n = 0
    for m in re.finditer(r"(?<![\w])" + kw + r"(?![\w])", g):
        ctx = g[max(0, m.start() - 150):m.start() + 150]
        # 筛掉 CSS/JS 属性
        if any(x in ctx for x in ("lipstick", "PlayerCombatMapper", "@typedef", "css", "filter:", "class=\"", "getPropertyValue")):
            continue
        n += 1
        if n > 4:
            break
        print(f"  @{m.start()}: {ctx!r}")
    if n == 0:
        print("  （全是 CSS/JS，无 UI 文本）")
