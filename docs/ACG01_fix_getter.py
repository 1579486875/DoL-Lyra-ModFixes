"""修 v3 的 getter：缓存函数，不要在 getter 里每次新建（会导致栈溢出）。"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

OLD_GET = '''            Object.defineProperty(st, name, {
                configurable: true,
                enumerable: true,
                get: function () { return makeFn(name); },
                set: function (v) {
                    if (typeof v === "function") {
                        HOLDER[name].orig = v;
                    }
                }
            });
            return true;'''

NEW_GET = '''            /* 缓存函数，避免每次访问都新建（会导致递归/栈溢出） */
            if (!HOLDER[name].fn) HOLDER[name].fn = makeFn(name);
            Object.defineProperty(st, name, {
                configurable: true,
                enumerable: true,
                get: function () { return HOLDER[name].fn; },
                set: function (v) {
                    if (typeof v === "function") {
                        HOLDER[name].orig = v;
                        HOLDER[name].fn = makeFn(name);   /* 重建一次，闭包里读到新 orig */
                    }
                }
            });
            return true;'''


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")

    hit = 0
    for a, b in ((H.escape(OLD_GET, quote=False), H.escape(NEW_GET, quote=False)),
                 (OLD_GET, NEW_GET)):
        if a in data:
            n = data.count(a)
            data = data.replace(a, b)
            hit += n
            print(f"  ✅ 替换 {n} 处 getter")
            break

    if not hit:
        print("❌ 未找到旧 getter")
        # 诊断
        i = data.find("Object.defineProperty(st, name")
        if i > 0:
            print(repr(data[max(0, i - 200):i + 600]))
        return 1

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
