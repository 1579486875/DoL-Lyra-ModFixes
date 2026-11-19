"""查 modded 独有的 2 处 set/run/print 内含 <<。"""
import html
import re
import zipfile

MODDED = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VANILLA = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(apk):
    z = zipfile.ZipFile(apk)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    out = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        out[html.unescape(m.group(1))] = html.unescape(m.group(2))
    return out


mb = load(MODDED)
vb = load(VANILLA)

for pn in ("Widgets Wraith", "Widgets speech-Robin"):
    print("=" * 94)
    print(f"{pn}")
    print("=" * 94)

    def dump(blocks, label):
        b = blocks.get(pn, "")
        print(f"\n--- {label} (长度 {len(b)}) ---")
        for m in re.finditer(r"<<(set|run|print|=)\b", b):
            i = m.end()
            depth = 1
            while i < len(b) and depth > 0:
                if b.startswith("<<", i):
                    depth += 1
                    i += 2
                elif b.startswith(">>", i):
                    depth -= 1
                    i += 2
                else:
                    i += 1
            expr = b[m.end():i - 2]
            e = re.sub(r'"[^"]*"', '""', expr)
            e = re.sub(r"'[^']*'", "''", e)
            e = re.sub(r"`[^`]*`", "``", e)
            if "<<" in e:
                print(f"  ⚠️ <<{m.group(1)} {expr[:200]!r}")
                print(f"      原文: {b[max(0,m.start()-80):m.start()+400]!r}")

    dump(vb, "vanilla")
    dump(mb, "modded")
    print()
