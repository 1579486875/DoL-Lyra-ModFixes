"""查 vanilla 有、modded 消失的 9 种 includes 判断，判断真假。"""
import html
import re
import zipfile

MOD = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"

TARGETS = ["fifth", "fourth", "locker", "metal", "pale", "pet", "second",
           "some orphan", "third"]


def load(p):
    z = zipfile.ZipFile(p)
    return html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


vg = load(VAN)
mg = load(MOD)

for t in TARGETS:
    print("=" * 94)
    print(f"{t!r}")
    print("=" * 94)
    print("--- vanilla 的判断 ---")
    for m in list(re.finditer(r'\.\s*includes\(\s*["\']' + re.escape(t) + r'["\']\s*\)', vg))[:3]:
        print(f"  {vg[max(0,m.start()-200):m.start()+120]!r}")
    print("\n--- modded 里该判断是否还在 ---")
    n = len(re.findall(r'\.\s*includes\(\s*["\']' + re.escape(t) + r'["\']\s*\)', mg))
    print(f"  剩余 {n} 处")
    if n == 0:
        # 找 modded 里对应的中文
        print("  在 modded 里找可能的中文替换:")
        # 从 vanilla 上下文提取字段名
        m = re.search(r'([\w$.\[\]]+)\.\s*includes\(\s*["\']' + re.escape(t) + r'["\']\s*\)', vg)
        if m:
            field = m.group(1)
            print(f"    字段: {field}")
            # 找 modded 里该字段的比较值
            vals = set(re.findall(re.escape(field) + r'\s*(?:is|===)\s*["\']([^"\']{1,20})["\']', mg))
            print(f"    modded 该字段的比较值: {sorted(vals)[:10]}")
    print()
