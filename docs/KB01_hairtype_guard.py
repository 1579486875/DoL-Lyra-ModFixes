"""第 7 轮：给 i18n 引入的 $fringetypeCN / $hairtypeCN 加兜底。

现状（i18n 作者写的）：
  <<run setup.hairstyles.fringe.forEach(style => {if (V.fringetype == style.variable) V.fringetypeCN = style.name_cap;})>>
  目前，你的刘海是<span class="gold">$fringetypeCN</span>，...

风险：如果 V.fringetype 不在 setup.hairstyles.fringe 里（模组加了自定义发型、
      或老存档存了已删除的发型名），$fringetypeCN 就是 undefined。

修法：显示处加兜底，不改变原有功能意图。

注意：index.html 里只有 < > 被转义，引号是原样的。
"""
import html as H
import os
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

PAIRS = [
    ('<span class="gold">$fringetypeCN</span>',
     '<span class="gold">${$fringetypeCN || "自然下垂"}</span>'),
    ('<span class="gold">$hairtypeCN</span>',
     '<span class="gold">${$hairtypeCN || "自然下垂"}</span>'),
]


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    ok = 0
    for old, new in PAIRS:
        e_old = H.escape(old, quote=False)
        e_new = H.escape(new, quote=False)
        if e_old in data:
            n = data.count(e_old)
            data = data.replace(e_old, e_new)
            ok += 1
            print(f"  ✅ 转义形态 ({n} 处)  {old[:55]!r}")
        elif old in data:
            n = data.count(old)
            data = data.replace(old, new)
            ok += 1
            print(f"  ✅ 未转义 ({n} 处)  {old[:55]!r}")
        else:
            print(f"  （未命中）{old[:60]!r}")
            # 打印实际形态帮助诊断
            i = data.find("$fringetypeCN")
            if i >= 0:
                print(f"       实际: {data[max(0,i-60):i+60]!r}")

    print(f"\n命中 {ok} / {len(PAIRS)}")
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
