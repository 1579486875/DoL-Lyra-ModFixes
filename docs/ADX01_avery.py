"""查 Pub Avery Stones Angry 段落是否真丢失 $avery_state 分支。"""
import html
import re
import zipfile


def get(p, pn):
    z = zipfile.ZipFile(p)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    for m in re.finditer(r'<tw-passagedata([^>]*)>(.*?)</tw-passagedata>', raw, re.S):
        nm = re.search(r'name="([^"]+)"', m.group(1))
        if nm and html.unescape(nm.group(1)) == pn:
            return html.unescape(m.group(2))
    return ""


MOD = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"

PN = "Pub Avery Stones Angry"
mv = get(MOD, PN)
vv = get(VAN, PN)

print("=" * 88)
print(f"{PN}")
print("=" * 88)
print(f"  vanilla 长度 {len(vv):,}   modded 长度 {len(mv):,}")
print(f"  vanilla 有 $avery_state: {'$avery_state' in vv}")
print(f"  modded  有 $avery_state: {'$avery_state' in mv}")

print("\n[vanilla 全文]")
print(vv)
print("\n[modded 全文]")
print(mv)

# 统计段落里 if 的数量
print("\n=== 结构对比 ===")
for label, t in (("vanilla", vv), ("modded", mv)):
    print(f"  {label}: <<if>> {len(re.findall(r'<<if\\b', t))}  <</if>> {t.count('<</if>>')}  "
          f"<<link>> {len(re.findall(r'<<link\\b', t))}")
