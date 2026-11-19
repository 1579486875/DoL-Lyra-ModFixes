"""构建收尾守卫：检查并修复 widget 嵌套。

任何 <<widget>> 内部都不允许再出现 <<widget>>。
如果发现，把内层的整个块剪切出来，放到外层闭合之后。
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    total_fixed = 0

    for _ in range(10):  # 最多修 10 轮
        # 找外层 widget 的起点，然后检查内部是否还有 widget
        fixed_this_round = False
        for m in re.finditer(r'&lt;&lt;widget\s+"([^"]+)"&gt;&gt;', data):
            open_pos = m.start()
            # 找它的闭合（第一个不在嵌套内的 </widget>）
            i = m.end()
            depth = 1
            inner_widget = None
            while i < len(data) and depth > 0:
                if data.startswith('&lt;&lt;widget ', i):
                    depth += 1
                    if inner_widget is None and depth == 2:
                        inner_widget = i
                    i += 14
                elif data.startswith('&lt;&lt;/widget&gt;&gt;', i):
                    depth -= 1
                    if depth == 0:
                        break
                    i += 17
                else:
                    i += 1

            if inner_widget is None:
                continue

            # 找到了嵌套：把内层整块剪出来
            name = m.group(1)
            j = inner_widget
            d2 = 1
            while j < len(data):
                if data.startswith('&lt;&lt;widget ', j):
                    d2 += 1
                    j += 14
                elif data.startswith('&lt;&lt;/widget&gt;&gt;', j):
                    d2 -= 1
                    if d2 == 0:
                        j += 17
                        break
                    j += 17
                else:
                    j += 1
            if d2 != 0:
                print(f"  ⚠️ {name} 内的嵌套块没找到闭合")
                break

            block = data[inner_widget:j]
            data = data[:inner_widget] + data[j:]
            # 插到外层闭合之后
            k = data.find('&lt;&lt;/widget&gt;&gt;', open_pos)
            if k < 0:
                break
            k += 17
            data = data[:k] + "\n" + block + data[k:]
            total_fixed += 1
            print(f"  ✅ 已把嵌套在 {name} 里的 widget 移出")
            fixed_this_round = True
            break

        if not fixed_this_round:
            break

    if total_fixed:
        open(HTML, "wb").write(data.encode("utf-8"))
        print(f"\n合计修复 {total_fixed} 处")
    else:
        print("  ✅ 无 widget 嵌套")

    # 校验
    g = H.unescape(data)
    bad = 0
    for m in re.finditer(r'<<widget\s+"([^"]+)"\s*>>(.*?)<</widget>>', g, re.S):
        if "<<widget" in m.group(2):
            bad += 1
            print(f"  ❌ {m.group(1)}")
    print(f"\n核对：嵌套 widget {bad}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
