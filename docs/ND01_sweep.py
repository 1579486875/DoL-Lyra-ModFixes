"""全库排查：字符串里内嵌宏 / 函数参数里的裸 TwineScript / 全角符号。

这是"尽全力"的兜底扫描，覆盖前面所有修过的模式。
"""
import html
import re
from collections import Counter

HTML = r"E:\TAML\_dol\work\index_modded6.html"
VANILLA = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(path):
    import zipfile
    if path.endswith(".apk"):
        z = zipfile.ZipFile(path)
        raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    else:
        raw = open(path, "rb").read().decode("utf-8", "replace")
    out = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        out[html.unescape(m.group(1))] = html.unescape(m.group(2))
    return out


mb = load(HTML)
vb = load(VANILLA)
g = "\n".join(mb.values())
vg = "\n".join(vb.values())

print("=" * 94)
print("A) <<set>> 的字符串字面量里含 <<（显示时会字面输出）")
print("=" * 94)


def find_set_literal_macro(text):
    hits = []
    # <<set X to "..."...>>  —— 只看纯字符串（不含 + 拼接）
    pat = re.compile(r'<<set\s+[\w$_.\[\]]+\s+to\s+("(?:[^"\\]|\\.)*")\s*>>')
    for m in pat.finditer(text):
        lit = m.group(1)
        if "<<" in lit:
            hits.append(m.group(0)[:170])
    return hits


m_hits = find_set_literal_macro(g)
v_hits = find_set_literal_macro(vg)
print(f"  modded: {len(m_hits)}   vanilla: {len(v_hits)}")
for x in m_hits[:12]:
    print(f"    {x!r}")

print("\n" + "=" * 94)
print("B) either()/random() 参数里的全角逗号（字符串外）")
print("=" * 94)


def find_fw_comma(text):
    hits = []
    for fn in ("either", "random"):
        for m in re.finditer(r"<<print\s+" + fn + r"\(", text):
            i = m.end()
            depth = 1
            in_str, q = False, ""
            while i < len(text) and depth > 0:
                ch = text[i]
                if in_str:
                    if ch == "\\":
                        i += 2
                        continue
                    if ch == q:
                        in_str = False
                    i += 1
                    continue
                if ch in "`'\"":
                    in_str, q = True, ch
                    i += 1
                    continue
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                i += 1
            body = text[m.end():i - 1]
            # 检查字符串外的全角逗号
            j, in_s, qq = 0, False, ""
            while j < len(body):
                ch = body[j]
                if in_s:
                    if ch == "\\":
                        j += 2
                        continue
                    if ch == qq:
                        in_s = False
                    j += 1
                    continue
                if ch in "`'\"":
                    in_s, qq = True, ch
                    j += 1
                    continue
                if ch == "，":
                    hits.append(m.group(0)[:130])
                    break
                j += 1
    return hits


m_fw = find_fw_comma(g)
v_fw = find_fw_comma(vg)
print(f"  modded: {len(m_fw)}   vanilla: {len(v_fw)}")
for x in m_fw[:10]:
    print(f"    {x!r}")

print("\n" + "=" * 94)
print("C) either() 参数里的裸 TwineScript（含 << 但无引号）")
print("=" * 94)


def find_bare_macro_arg(text):
    hits = []
    for m in re.finditer(r"<<print\s+either\(", text):
        i = m.end()
        depth = 1
        in_str, q = False, ""
        while i < len(text) and depth > 0:
            ch = text[i]
            if in_str:
                if ch == "\\":
                    i += 2
                    continue
                if ch == q:
                    in_str = False
                i += 1
                continue
            if ch in "`'\"":
                in_str, q = True, ch
                i += 1
                continue
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            i += 1
        body = text[m.end():i - 1]
        parts, buf, d2, in_s, qq = [], "", 0, False, ""
        for ch in body:
            if in_s:
                buf += ch
                if ch == qq:
                    in_s = False
                continue
            if ch in "`'\"":
                in_s, qq = True, ch
                buf += ch
                continue
            if ch in "([{":
                d2 += 1
            elif ch in ")]}":
                d2 -= 1
            if ch == "," and d2 == 0:
                parts.append(buf)
                buf = ""
                continue
            buf += ch
        if buf.strip():
            parts.append(buf)
        for p in parts:
            s = p.strip()
            if s and "<<" in s and not s.startswith(("`", '"', "'")) and " ? " not in s:
                hits.append(m.group(0)[:130] + " ... " + s[:60])
    return hits


m_bare = find_bare_macro_arg(g)
v_bare = find_bare_macro_arg(vg)
print(f"  modded: {len(m_bare)}   vanilla: {len(v_bare)}")
for x in m_bare[:10]:
    print(f"    {x!r}")

print("\n" + "=" * 94)
print("D) 汇总")
print("=" * 94)
total_m = len(m_hits) + len(m_fw) + len(m_bare)
total_v = len(v_hits) + len(v_fw) + len(v_bare)
print(f"  modded 待修: {total_m}")
print(f"  vanilla 基线: {total_v}")
print(f"  我引入的: {total_m - total_v}")
