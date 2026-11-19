"""第 4-6 轮：修复 i18n 引入的变量 bug（精确版）。

1) $compoundWraith —— i18n 把 $compound 改成 $compoundWraith，后者从未定义（3 处）
2) <<if worn.handheld. —— i18n 把 $worn 的 $ 丢了（1 处，Gwylan Walk School Solo）

⚠️ 绝不能全局替换 worn.xxx：裸 worn 有 1202 处，绝大多数是 JS 局部变量。
⚠️ 文件里宏是 HTML 转义形态 &lt;&lt;if，正则要同时兼容两种。
"""
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    ok = 0

    # 1) $compoundWraith -> $compound
    n = data.count("$compoundWraith")
    if n:
        data = data.replace("$compoundWraith", "$compound")
        ok += 1
        print(f"✅ $compoundWraith -> $compound : {n} 处")

    # 2) <<if worn.handheld. -> <<if $worn.handheld.
    fixed = 0
    for pat_src, repl in (
        (r"(&lt;&lt;if\s+)worn\.handheld\.", r"\1$worn.handheld."),
        (r"(<<if\s+)worn\.handheld\.", r"\1$worn.handheld."),
    ):
        pat = re.compile(pat_src)
        cnt = len(pat.findall(data))
        if cnt:
            data = pat.sub(repl, data)
            fixed += cnt
            print(f"   （{pat_src[:20]}... 命中 {cnt} 处）")
    if fixed:
        ok += 1
        print(f"✅ <<if worn.handheld. -> <<if $worn.handheld. : {fixed} 处")
    else:
        print("（<<if worn.handheld 未找到，可能已修）")

    # 校验
    total_bare = len(re.findall(r"(?<![\w$])worn\.", data))
    print(f"   改后裸 worn. 共 {total_bare} 处")

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"\n命中 {ok} 组修复")
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
