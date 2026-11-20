"""F02：对比基线 —— 这些宏配对问题是不是原版就有的。"""
import html as H
import os
import re
import zipfile
from collections import Counter

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
ARCHIVE = r"E:\TAML\_dol\archive"
GOOD = os.path.join(ARCHIVE, "DoL-Lyra-0.5.12.13-CHS-modded_20261120-061313_修复arsc可安装.apk")
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def get_passages_from(path, is_apk=True):
    raw = zipfile.ZipFile(path).read("assets/www/index.html").decode("utf-8", "replace")
    out = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        out[m.group(1)] = H.unescape(m.group(2))
    return out


def check_pairs(body):
    """返回 (多余闭合列表, 未闭合列表)。"""
    PAIRED = {"if", "for", "widget", "switch", "link", "button",
              "script", "silently", "nobr", "capture"}
    extra = []
    stack = []
    i = 0
    L = len(body)
    while i < L:
        j = body.find("<<", i)
        if j < 0:
            break
        # 跳过 <<-- 注释 -->>
        if body.startswith("<<--", j):
            k = body.find("-->>", j + 4)
            i = k + 4 if k > 0 else L
            continue
        # 跳过 <<= expr>>
        if j + 2 < L and body[j + 2] == "=":
            k = body.find(">>", j + 3)
            i = k + 2 if k > 0 else L
            continue
        k = body.find(">>", j + 2)
        if k < 0:
            break
        macro = body[j:k + 2]
        i = k + 2
        mm = re.match(r"<<\s*(/?)\s*([A-Za-z_][A-Za-z0-9_\-]*)", macro)
        if not mm:
            continue
        is_close = mm.group(1) == "/"
        name = mm.group(2).lower()
        if name in ("else", "elseif", "break", "continue", "case", "default",
                    "run", "set", "print", "include", "display", "goto"):
            continue
        if name in PAIRED:
            if is_close:
                if stack and stack[-1] == name:
                    stack.pop()
                else:
                    extra.append((name, j, macro[:60]))
            else:
                stack.append(name)
    return extra, stack


print("=" * 100)
print("对比三个版本的宏配对问题")
print("=" * 100)

for label, path in (("vanilla（Lyra 原包）", VAN),
                    ("0A316E37（修复前基线）", GOOD),
                    ("当前包", APK)):
    try:
        ps = get_passages_from(path)
    except Exception as e:
        print(f"\n[{label}] 读取失败: {e}")
        continue
    tot_extra = 0
    tot_unclosed = 0
    bad_passages = []
    for pname, body in ps.items():
        ex, st = check_pairs(body)
        if ex or st:
            tot_extra += len(ex)
            tot_unclosed += len(st)
            bad_passages.append((pname, len(ex), len(st)))
    print(f"\n[{label}]  passage {len(ps)}")
    print(f"    多余闭合 {tot_extra} / 未闭合 {tot_unclosed}  (涉及 {len(bad_passages)} 个 passage)")

print("\n" + "=" * 100)
print("当前包 vs 基线的差异 passage")
print("=" * 100)
cur = get_passages_from(APK)
base = get_passages_from(GOOD)
diff = []
for pname in cur:
    if pname not in base:
        continue
    ce, cs = check_pairs(cur[pname])
    be, bs = check_pairs(base[pname])
    if len(ce) != len(be) or len(cs) != len(bs):
        diff.append((pname, len(be), len(bs), len(ce), len(cs)))

print(f"  配对状态变化的 passage: {len(diff)}")
for pname, be, bs, ce, cs in diff[:20]:
    print(f"    [{pname}] 基线({be}多/{bs}未) -> 当前({ce}多/{cs}未)")
