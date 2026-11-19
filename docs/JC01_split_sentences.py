"""翻译被 HTML 标签拆开的 2 句（片段级替换）。"""
import os
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

# (原文片段, 译文片段)
PAIRS = [
    # 1) <span class="gold">It's a brass statuette,</span> moulded in the shape of an eagle.
    ("""<span class="gold">It's a brass statuette,</span> moulded in the shape of an eagle.""",
     """<span class="gold">那是一尊黄铜小雕像，</span>铸成了鹰的形状。"""),
    ("""&lt;span class="gold"&gt;It's a brass statuette,&lt;/span&gt; moulded in the shape of an eagle.""",
     """&lt;span class="gold"&gt;那是一尊黄铜小雕像，&lt;/span&gt;铸成了鹰的形状。"""),

    # 2) You feel a <span @class="basicJitterCss()">strange heat</span> just beneath your skin.
    ("""You feel a <span @class="basicJitterCss()">strange heat</span> just beneath your skin.""",
     """你感到皮肤下泛起一阵<span @class="basicJitterCss()">异样的燥热</span>。"""),
    ("""You feel a &lt;span @class="basicJitterCss()"&gt;strange heat&lt;/span&gt; just beneath your skin.""",
     """你感到皮肤下泛起一阵&lt;span @class="basicJitterCss()"&gt;异样的燥热&lt;/span&gt;。"""),
]


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    ok = 0
    for en, cn in PAIRS:
        if en in data:
            n = data.count(en)
            data = data.replace(en, cn)
            ok += 1
            print(f"  ✅ {en[:70]!r}  ({n} 处)")
        else:
            print(f"  （未命中）{en[:70]!r}")

    print(f"\n命中 {ok} / {len(PAIRS)}")
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
