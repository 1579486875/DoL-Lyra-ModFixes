"""查这 6 个宏的正确名。"""
import html
import re
import zipfile

MOD = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def load(p):
    z = zipfile.ZipFile(p)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    return html.unescape(raw), raw


mg, mraw = load(MOD)
vg, vraw = load(VAN)

TARGETS = {
    "printNobody": ["printNobody", "printnobody", "print_nobody", "nobody"],
    "QUANTIFIER_OF_FOODS_CN": ["QUANTIFIER_OF_FOODS_CN", "quantifier_of_foods_cn",
                               "quantifierOfFoodsCn", "QUANTIFIER_OF_FOODS"],
    "UPDATE_CLOTH_CN": ["UPDATE_CLOTH_CN", "update_cloth_cn", "updateClothCn",
                        "update_cloth_cn_widget"],
    "temple_rank": ["temple_rank", "templerank", "templeRank"],
    "pcpet-name": ["pcpet-name", "pcpetname", "pcPetName"],
    "plural-ize": ["plural-ize", "pluralize", "pluralise"],
}

for bad, cands in TARGETS.items():
    print("=" * 88)
    print(f"{bad!r} 的正确名")
    print("=" * 88)
    for c in cands:
        md = len(re.findall(r'<<widget\s+"' + re.escape(c) + r'"', mg))
        vd = len(re.findall(r'<<widget\s+"' + re.escape(c) + r'"', vg))
        mc = len(re.findall(r"<<" + re.escape(c) + r"\b", mg))
        vc = len(re.findall(r"<<" + re.escape(c) + r"\b", vg))
        if md or vd or (mc and c != bad) or (vc and c != bad):
            print(f"  {c:<32} 定义 modded {md}/vanilla {vd}  调用 modded {mc}/vanilla {vc}")
    # 也查 Macro.add / DefineMacro
    for c in cands:
        if re.search(r'(?:Macro\.add|DefineMacro)\(\s*["\']' + re.escape(c) + r'["\']', mg):
            print(f"  {c}: Macro.add/DefineMacro 注册")
    print()
