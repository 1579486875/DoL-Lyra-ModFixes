"""修 <<script>> 的守卫条件：SugarCube.setup 不存在，应该直接用全局 setup。

vanilla 的写法是裸 setup.xxx = function(...)
我错写成 SugarCube.setup，导致 5 个 <<script>> 全部提前 return。
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

# 各种形态的守卫
GUARDS = [
    'if (!window.SugarCube || !SugarCube.setup) return;',
    'if (!window.SugarCube || !SugarCube.setup) return; ',
    'if(!window.SugarCube||!SugarCube.setup)return;',
]

REPLACE_GUARD = 'var st = (typeof setup !== "undefined" && setup) ? setup : (window.setup || (window.SugarCube && window.SugarCube.setup)); if (!st) return;'

# var st = SugarCube.setup;  /  var s = SugarCube.setup;
VAR_PAT = re.compile(r'var\s+(st|s)\s*=\s*SugarCube\.setup;')


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    g = H.unescape(data)
    total = 0

    # 1) 替换守卫
    for gd in GUARDS:
        for a, b in ((H.escape(gd, quote=False), H.escape(REPLACE_GUARD, quote=False)),
                     (gd, REPLACE_GUARD)):
            if a in data:
                n = data.count(a)
                # 特殊：`if(!...)return; var s=SugarCube.setup;` 这种连着的，要保留 var s
                if "var s=SugarCube.setup" in data and "return;" in gd:
                    pass
                data = data.replace(a, b)
                total += n
                print(f"  ✅ 替换守卫 {gd[:50]!r} ({n})")
                break

    # 2) 替换 var st = SugarCube.setup; -> var st = ...（已经是了则跳过）
    def fix_var(m):
        nonlocal total
        name = m.group(1)
        # 检查前面是否已经有新守卫
        start = m.start()
        ctx = data[max(0, start - 300):start]
        if 'typeof setup !== "undefined"' in ctx:
            # 已经有守卫，只需要把 SugarCube.setup 改成 setup（用已定义的 st）
            total += 1
            return f'var {name} = st;' if name != "st" else f'var {name} = st;'
        total += 1
        return f'var {name} = (typeof setup !== "undefined" && setup) ? setup : (window.setup || (window.SugarCube && window.SugarCube.setup));'

    data = VAR_PAT.sub(fix_var, data)

    # 3) 压缩形态 var s=SugarCube.setup
    data = data.replace("var s=SugarCube.setup", "var s=(typeof setup!==\"undefined\"&&setup)?setup:window.setup")

    print(f"\n合计 {total} 处")

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出 {HTML}  ({os.path.getsize(HTML):,} 字节)")

    # 校验
    g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
    print("\n=== 校验 ===")
    print(f"  残留 SugarCube.setup: {len(re.findall(r'SugarCube[.]setup', g2))}")
    for m in re.finditer(r"SugarCube\.setup", g2):
        ctx = g2[max(0, m.start() - 80):m.start() + 80]
        print(f"    {ctx!r}")
    print(f"  新守卫数量: {len(re.findall(chr(39) + 'typeof setup' + chr(39), g2))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
