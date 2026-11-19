"""只看 modded 独有的未定义 setup 符号，并区分「我加的」和「被翻坏的」。"""
import html
import re
import zipfile

MOD = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(p):
    z = zipfile.ZipFile(p)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    return html.unescape(raw)


mg = load(MOD)
vg = load(VAN)


def analyze(raw):
    refs = set(re.findall(r"setup\.(\w+)", raw))
    defs = set(re.findall(r"<<set\s+setup\.(\w+)\s*(?:to|=)", raw))
    defs |= set(re.findall(r"setup\.(\w+)\s*=[^=]", raw))
    defs |= set(re.findall(r'setup\[\s*["\'](\w+)["\']\s*\]\s*=', raw))
    defs |= {"test", "history"}
    return refs, defs, refs - defs


mr, md, mm = analyze(mg)
vr, vd, vm = analyze(vg)

only = sorted(mm - vm)
print("=" * 94)
print(f"modded 独有的未定义 setup.* ({len(only)} 个)")
print("=" * 94)

CJK = re.compile(r"[\u4e00-\u9fff]")
suspicious = []
known_added = []

for x in only:
    # 找引用上下文
    ctxs = []
    for m in list(re.finditer(r"setup\." + re.escape(x), mg))[:2]:
        ctxs.append(mg[max(0, m.start() - 130):m.start() + 130])

    if CJK.search(x):
        suspicious.append((x, ctxs))
    else:
        known_added.append((x, ctxs))

print("\n--- 含中文（极可能被翻坏）---")
for x, ctxs in suspicious:
    print(f"\n  setup.{x}")
    for c in ctxs:
        print(f"    {c!r}")

print("\n--- 纯英文（我加的或 i18n 引用的）---")
for x, ctxs in known_added:
    print(f"\n  setup.{x}")
    for c in ctxs[:1]:
        print(f"    {c[:220]!r}")
