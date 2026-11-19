"""查 2 个「从有中文变没中文」的 passage。"""
import html
import json
import re
import zipfile

OLD = r"C:\Users\asus\Downloads\DoL-Lyra-0.5.12.13-CHS-modded-11.18.apk"
NEW = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
I18N = r"E:\TAML\_dol\work\i18n_dict.json"

TARGETS = ["Monster Selection", "StoryRightSidebar"]


def get_passage(path, name):
    z = zipfile.ZipFile(path)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        if html.unescape(m.group(1)) == name:
            return html.unescape(m.group(2))
    return None


d = json.load(open(I18N, "r", encoding="utf-8"))
by_p = {}
for it in d["typeB"]["TypeBInputStoryScript"]:
    pn = it.get("pN")
    if pn in TARGETS:
        by_p.setdefault(pn, []).append(it)

for t in TARGETS:
    print("=" * 94)
    print(f"{t}")
    print("=" * 94)

    o = get_passage(OLD, t)
    n = get_passage(NEW, t)
    print(f"\n--- 昨天 (长度 {len(o) if o else 0}) ---")
    print(repr(o[:800]) if o else "未找到")
    print(f"\n--- 现在 (长度 {len(n) if n else 0}) ---")
    print(repr(n[:800]) if n else "未找到")

    print(f"\n--- i18n 条目 ({len(by_p.get(t, []))}) ---")
    for it in by_p.get(t, []):
        print(f"  pos={it.get('pos')}  f={it.get('f')[:120]!r}")
        print(f"              t={it.get('t')[:120]!r}")
    print()
