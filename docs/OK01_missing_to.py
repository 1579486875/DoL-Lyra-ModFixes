"""第 41 轮：全库找 <<set $var "value">> 缺 to 的语法错误（原版 bug）。"""
import html
import re
import zipfile

MODDED = r"E:\TAML\_dol\work\index_modded6.html"
VANILLA = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(path):
    if path.endswith(".apk"):
        z = zipfile.ZipFile(path)
        raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    else:
        raw = open(path, "rb").read().decode("utf-8", "replace")
    blocks = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        pn = html.unescape(m.group(1))
        b = html.unescape(m.group(2))
        for pat in (r"/\*.*?\*/", r"<!--.*?-->", r"/%.*?%/"):
            b = re.sub(pat, " ", b, flags=re.S)
        blocks[pn] = b
    return blocks


def extract_macros(text, pat):
    out = []
    for m in re.finditer(pat, text):
        i = m.end()
        depth = 1
        while i < len(text) and depth > 0:
            if text.startswith("<<", i):
                depth += 1
                i += 2
            elif text.startswith(">>", i):
                depth -= 1
                i += 2
            else:
                i += 1
        out.append((m.start(), text[m.end():i - 2]))
    return out


def find_missing_to(blocks):
    """<<set $var "..." >> 这种缺 to 的。"""
    out = []
    for pn, b in blocks.items():
        for pos, expr in extract_macros(b, r"<<set\b"):
            e = expr.strip()
            # 形如： $var "..."   或  $var '...'  或  $var 123
            if re.match(r'^\$[\w.\[\]]+\s+(".*"|\'.*\'|-?\d+(\.\d+)?)$', e, re.S):
                out.append((pn, e[:100]))
    return out


mb = load(MODDED)
vb = load(VANILLA)

mm = find_missing_to(mb)
vm = find_missing_to(vb)

print("=" * 94)
print("第 41 轮：<<set $var \"value\">> 缺 to")
print("=" * 94)
print(f"  modded: {len(mm)}   vanilla: {len(vm)}")
print()
for pn, e in mm:
    mark = "（原版也有）" if any(v[0] == pn and v[1] == e for v in vm) else "（可能本次引入）"
    print(f"  [{pn}] {e!r}  {mark}")
