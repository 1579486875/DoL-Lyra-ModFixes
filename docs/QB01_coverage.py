"""关键对比：把昨天的包也模拟应用 i18n，看两者最终翻译覆盖率谁高。"""
import html
import json
import re
import zipfile
from collections import Counter

OLD = r"C:\Users\asus\Downloads\DoL-Lyra-0.5.12.13-CHS-modded-11.18.apk"
NEW = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
I18N = r"E:\TAML\_dol\work\i18n_dict.json"


def load_blocks(path):
    z = zipfile.ZipFile(path)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    out = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        out[html.unescape(m.group(1))] = m.group(2)  # 保留转义
    return out


d = json.load(open(I18N, "r", encoding="utf-8"))
by_p = {}
for it in d["typeB"]["TypeBInputStoryScript"]:
    pn = it.get("pN")
    if pn:
        by_p.setdefault(pn, []).append(it)


def apply_i18n(blocks):
    """模拟 I18nTweeReplacer 的运行时行为。"""
    out = {}
    ok = skip = 0
    for pn, body_esc in blocks.items():
        lst = by_p.get(pn)
        if not lst:
            out[pn] = body_esc
            continue
        body = html.unescape(body_esc)
        for it in sorted(lst, key=lambda x: x.get("pos") or 0, reverse=True):
            f, t = it.get("f"), it.get("t")
            if not f or t is None:
                continue
            pos = it.get("pos", -1)
            if 0 <= pos <= len(body) and body[pos:pos + len(f)] == f:
                body = body[:pos] + t + body[pos + len(f):]
                ok += 1
            elif f in body:
                body = body.replace(f, t, 1)
                ok += 1
            else:
                skip += 1
        out[pn] = html.escape(body, quote=False)
    return out, ok, skip


print("加载昨天的包...")
ob = load_blocks(OLD)
print(f"  passage: {len(ob)}")
oa, ook, oskip = apply_i18n(ob)
print(f"  模拟 i18n 应用: 成功 {ook}  失配 {oskip}")

print("\n加载现在的包...")
nb = load_blocks(NEW)
print(f"  passage: {len(nb)}")

print("\n" + "=" * 94)
print("翻译覆盖率对比（按 passage 的中文字符数）")
print("=" * 94)


def cjk_stats(blocks):
    total = 0
    zero = 0
    per = {}
    for pn, b in blocks.items():
        g = html.unescape(b)
        c = len(re.findall(r"[\u4e00-\u9fff]", g))
        per[pn] = c
        total += c
        if c == 0:
            zero += 1
    return per, total, zero


op, ot, oz = cjk_stats(oa)
np_, nt, nz = cjk_stats(nb)

print(f"  昨天（模拟运行时）: 中文 {ot:,} 字，零中文 passage {oz}")
print(f"  现在（已烤入）    : 中文 {nt:,} 字，零中文 passage {nz}")
print(f"  差值              : {nt - ot:+,} 字")

print("\n" + "=" * 94)
print("昨天有中文、现在没有的 passage（前 25 个）")
print("=" * 94)
lost = [(pn, op.get(pn, 0), np_.get(pn, 0)) for pn in op if op[pn] > 0 and np_.get(pn, 0) == 0]
lost.sort(key=lambda x: -x[1])
print(f"  共 {len(lost)} 个")
for pn, o, n in lost[:25]:
    print(f"    昨天 {o:>5} 字  现在 0    {pn}")

print("\n" + "=" * 94)
print("中文明显变少的 passage（前 25 个）")
print("=" * 94)
diff = [(pn, op.get(pn, 0), np_.get(pn, 0)) for pn in op if op[pn] > 0 and np_.get(pn, 0) > 0]
diff = [x for x in diff if x[2] < x[1] * 0.5]
diff.sort(key=lambda x: -(x[1] - x[2]))
print(f"  共 {len(diff)} 个（现在不足昨天一半）")
for pn, o, n in diff[:25]:
    print(f"    昨天 {o:>6}  现在 {n:>6}  少了 {o-n:>6}  {pn}")
