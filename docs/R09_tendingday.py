"""第 9 轮：查 tendingDay 那条注释的 // 是不是被 i18n 吃了。"""
import html
import re
import zipfile

MOD = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(p):
    z = zipfile.ZipFile(p)
    return html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


mg = load(MOD)
vg = load(VAN)

print("=" * 88)
print("modded tendingDay 附近")
print("=" * 88)
for m in re.finditer(r"parser don'?t? ?parse", mg):
    print(f"  @{m.start()}")
    print(f"  {mg[max(0,m.start()-200):m.start()+250]!r}")
    print()

print("=" * 88)
print("vanilla tendingDay 附近")
print("=" * 88)
for m in re.finditer(r"parser don'?t? ?parse", vg):
    print(f"  @{m.start()}")
    print(f"  {vg[max(0,m.start()-200):m.start()+250]!r}")
    print()

print("=" * 88)
print("搜索所有「<<script>> 紧跟英文注释」的模式")
print("=" * 88)
# 合法：<<script>>\n（空白）// 或 /* 或代码
# 非法：<<script>> 后面直接跟英文单词（无 // 无 /*）
BAD = re.compile(r"<<script>>[ \t]*([A-Za-z][^\n<]{10,120})")
for label, g in (("modded", mg), ("vanilla", vg)):
    print(f"\n[{label}]")
    n = 0
    for m in BAD.finditer(g):
        line = m.group(1).strip()
        # 排除合法的 JS 关键字开头
        if re.match(r"^(var|let|const|function|if|for|while|return|try|switch|"
                    r"document|window|jQuery|\$|setup|V\.|C\.|T\.|State|Engine|"
                    r"Macro|SugarCube|new |this\.|output|/\*|//)", line):
            continue
        n += 1
        if n <= 12:
            print(f"  @{m.start()}: {line[:110]!r}")
    print(f"  共 {n} 处可疑")
