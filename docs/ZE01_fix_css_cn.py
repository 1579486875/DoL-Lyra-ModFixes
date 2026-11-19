"""修 CSS 类名 / 变量名被翻译破坏 + 加通用检测。

已知：
  settings头部er        -> settingsHeader
  $featsBoosts.up成绩。 -> $featsBoosts.upgrades.
通用：$obj.xxx。yyy（全角句号出现在变量路径里 = 非法 JS）
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

FIXES = [
    ('class="settings头部er"', 'class="settingsHeader"'),
    ("'settings头部er'", "'settingsHeader'"),
    ('$featsBoosts.up成绩。', '$featsBoosts.upgrades.'),
]


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    total = 0
    for old, new in FIXES:
        for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
            if a in data:
                n = data.count(a)
                data = data.replace(a, b)
                total += n
                print(f"  ✅ {old!r} -> {new!r}  ({n})")
                break

    if total:
        open(HTML, "wb").write(data.encode("utf-8"))
        print(f"\n合计 {total} 处")

    g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
    CJK = re.compile(r"[\u4e00-\u9fff]")

    print("\n" + "=" * 90)
    print("通用检测：变量路径里的全角标点 / 中文")
    print("=" * 90)
    # $a.b。c  / $a.b，c  / $a.中文
    pat = re.compile(r"\$[\w$]+(?:\.[\w$]*[。，、；：！？][\w$]*)+")
    hits = set(pat.findall(g))
    # 也查 $a.中文
    hits |= set(re.findall(r"\$[\w$]+\.([\u4e00-\u9fff]+)(?=[\s\]\)\>,|&;.]|$)", g))
    if hits:
        print(f"  ❌ {len(hits)} 种")
        for h in sorted(hits)[:15]:
            print(f"    {h}")
    else:
        print("  ✅ 0 种")

    print("\n" + "=" * 90)
    print("检测：class / id 里的中文")
    print("=" * 90)
    css = []
    for m in re.finditer(r'(?:class|id)="([^"]{0,200})"', g):
        v = m.group(1)
        if CJK.search(v):
            css.append(v)
    for v in sorted(set(css)):
        print(f"  ⚠️ {v[:100]!r}")

    print("\n" + "=" * 90)
    print("检测：标识符里连续中文（变量名/属性名被翻）")
    print("=" * 90)
    # 形如 xxx中文yyy 的标识符（前后都是 ASCII 字母）
    idbad = set(re.findall(r"\b([A-Za-z_]\w*[\u4e00-\u9fff]+\w*)", g))
    # 排除正常的（$ 前缀的中文文本、URL 等）
    idbad = {x for x in idbad if not x.startswith("$") and len(x) < 50}
    if idbad:
        print(f"  ⚠️ {len(idbad)} 种")
        for x in sorted(idbad)[:20]:
            print(f"    {x!r}")
    else:
        print("  ✅ 0 种")
    return 0


if __name__ == "__main__":
    sys.exit(main())
