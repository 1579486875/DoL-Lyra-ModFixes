"""修剩下 10 个英文 displayName（作弊菜单的角色创建配置项）。"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

# 英文 displayName -> 中文
MAP = {
    "Body size:": "体型大小：",
    "Demeanour:": "举止：",
    "Breast sensitivity:": "胸部敏感度：",
    "Genital sensitivity:": "生殖器敏感度：",
    "Mouth sensitivity:": "口腔敏感度：",
    "Bottom sensitivity:": "后穴敏感度：",
    "Alcohol tolerance:": "酒精耐受度：",
    "Eye colour:": "瞳色：",
    "Hair colour:": "发色：",
    "Hair length:": "发长：",
    "Cheat mode:": "作弊模式：",
    "Condoms:": "安全套：",
    "Genitals:": "生殖器：",
    "Gender:": "性别：",
    "Penis size:": "阴茎大小：",
    "Breast size:": "胸部尺寸：",
    "Skin colour:": "肤色：",
    "Hair style:": "发型：",
    "Fringe style:": "刘海样式：",
    "Body shape:": "身形：",
    "Body type:": "体型：",
    "Awareness:": "意识：",
    "Background:": "角色背景：",
}


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    total = 0

    for en, cn in MAP.items():
        for a, b in ((f'displayName: "{en}"', f'displayName: "{cn}"'),
                     (H.escape(f'displayName: "{en}"', quote=False),
                      H.escape(f'displayName: "{cn}"', quote=False))):
            if a in data:
                n = data.count(a)
                data = data.replace(a, b)
                total += n
                print(f"  ✅ {en!r} -> {cn!r}  ({n})")
                break

    if total:
        open(HTML, "wb").write(data.encode("utf-8"))
        print(f"\n合计 {total} 处")
    else:
        print("（无改动）")

    # 校验
    g = H.unescape(data)
    remain = re.findall(r'displayName:\s*"([A-Za-z][^"]{1,40})"', g)
    print(f"\n剩余纯英文 displayName: {len(remain)}")
    for r in sorted(set(remain)):
        print(f"  {r!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
