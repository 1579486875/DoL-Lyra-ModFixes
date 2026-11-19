"""精确找被翻译破坏的标识符。

判据：对 `$obj.xxx`，取 xxx 的**最长 ASCII 前缀**：
  - 前缀在 vanilla 的属性集合里  -> 正常（xxx 后面的中文是普通文本）
  - 前缀不在 vanilla 里，且 xxx 含中文 -> 属性名被翻译
"""
import html as H
import os
import re
import sys
from collections import defaultdict

VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"
HTML = r"E:\TAML\_dol\work\index_modded6.html"

CJK = re.compile(r"[\u4e00-\u9fff]")


def load_apk(p):
    import zipfile
    z = zipfile.ZipFile(p)
    return H.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


def main():
    print("加载 vanilla...")
    vg = load_apk(VAN)
    v_by_obj = defaultdict(set)
    for o, p in re.findall(r"\$(\w+)\.(\w+)", vg):
        v_by_obj[o].add(p)
    print(f"  {len(v_by_obj)} 个对象")

    print("加载 modded...")
    mg = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))

    # 找所有 $obj.xxx（xxx 可含中文）
    suspects = []
    for m in re.finditer(r"\$(\w+)\.([\w\u4e00-\u9fff]+)", mg):
        o, x = m.group(1), m.group(2)
        if not CJK.search(x):
            continue
        # 取最长 ASCII 前缀
        mm = re.match(r"([A-Za-z_][A-Za-z0-9_]*)", x)
        prefix = mm.group(1) if mm else ""
        vset = v_by_obj.get(o, set())
        if prefix and prefix in vset:
            continue  # 正常：$obj.prop + 中文文本
        suspects.append((o, x, prefix, sorted(vset)[:8]))

    print(f"\n=== 可疑：属性名被翻译（{len(suspects)} 处）===")
    seen = set()
    for o, x, prefix, vset in suspects:
        key = (o, x)
        if key in seen:
            continue
        seen.add(key)
        print(f"  ${o}.{x}   (ASCII 前缀: {prefix!r})")
        print(f"     vanilla 该对象的属性示例: {vset}")

    # 尝试自动修复：vanilla 里有同对象、以 prefix 开头的唯一候选
    print("\n=== 自动匹配 ===")
    fixes = {}
    for o, x, prefix, _ in suspects:
        if not prefix:
            continue
        vset = v_by_obj.get(o, set())
        cands = [v for v in vset if v.lower().startswith(prefix.lower()) and v != prefix]
        if len(cands) == 1:
            fixes[(o, x)] = cands[0]
            print(f"  ${o}.{x} -> ${o}.{cands[0]}")
        else:
            print(f"  ${o}.{x}  候选 {cands[:5]}  （需人工确认）")

    # 手工确认的
    MANUAL = {("avery_mansion", "鞠躬"): "bow"}
    for (o, x), v in MANUAL.items():
        req = f"${o}.{x}"
        if req in mg:
            fixes[(o, x)] = v
            print(f"  [手工] ${o}.{x} -> ${o}.{v}")

    # 执行
    if fixes:
        print("\n=== 执行替换 ===")
        data = open(HTML, "rb").read().decode("utf-8", "replace")
        total = 0
        for (o, x), v in fixes.items():
            for a, b in ((H.escape(f"${o}.{x}", quote=False), H.escape(f"${o}.{v}", quote=False)),
                         (f"${o}.{x}", f"${o}.{v}")):
                if a in data:
                    n = data.count(a)
                    data = data.replace(a, b)
                    total += n
                    print(f"  ✅ ${o}.{x} -> ${o}.{v}  ({n} 处)")
                    break
        if total:
            open(HTML, "wb").write(data.encode("utf-8"))
            print(f"\n合计 {total} 处")
    else:
        print("\n（无需修复）")

    # 校验
    g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
    remain = []
    for m in re.finditer(r"\$(\w+)\.([\w\u4e00-\u9fff]+)", g):
        o, x = m.group(1), m.group(2)
        if not CJK.search(x):
            continue
        mm = re.match(r"([A-Za-z_][A-Za-z0-9_]*)", x)
        prefix = mm.group(1) if mm else ""
        if prefix and prefix in v_by_obj.get(o, set()):
            continue
        remain.append(f"${o}.{x}")
    print(f"\n剩余可疑: {len(set(remain))}")
    for r_ in sorted(set(remain))[:10]:
        print(f"  {r_}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
