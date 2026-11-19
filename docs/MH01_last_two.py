"""补齐剩余 2 处 either 反引号 + Wraith 内嵌宏（兼容 HTML 转义形态）。"""
import html as H
import os
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

PAIRS = [
    ('`你出手击中，<<He>>痛得缩了一下。"呃啊！"`，\n\t\t\t\t<<He>>挨了你一下，往后缩去。',
     '`你出手击中，<<He>>痛得缩了一下。"呃啊！"`,\n\t\t\t\t`<<He>>挨了你一下，往后缩去。`'),

    ('`<<He>>咯咯笑起来。"听起来好下流。"`，\n\t\t\t\t\t<<He>>尴尬地笑了笑。“你、你说这种话都不会不好意思吗？”',
     '`<<He>>咯咯笑起来。"听起来好下流。"`,\n\t\t\t\t\t`<<He>>尴尬地笑了笑。“你、你说这种话都不会不好意思吗？”`'),

    ('<<set _speechWraith to "_speaks。\\"_line1<<= _line2>>\\"">>',
     '<<set _speechWraith to "_speaks。" + "\\"" + "_line1" + _line2 + "\\"">>'),
]


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    ok = 0
    for old, new in PAIRS:
        hit = False
        for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
            if a in data:
                n = data.count(a)
                data = data.replace(a, b)
                ok += 1
                hit = True
                print(f"  ✅ ({n} 处) {old[:55]!r}")
                break
        if not hit:
            print(f"  ❌ {old[:70]!r}")
            # 诊断：找关键词附近
            key = old[:20]
            idx = data.find(H.escape(key[:8], quote=False))
            if idx < 0:
                idx = data.find(key[:8])
            if idx >= 0:
                print(f"      实际: {data[max(0,idx-80):idx+220]!r}")

    print(f"\n命中 {ok} / {len(PAIRS)}")
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
