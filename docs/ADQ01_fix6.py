"""修 6 个「调用了但不存在」的宏。

1) <<printNobody>>          -> 无人          (86 处，i18n 把 Nobody 当宏)
2) <<pcpet-name ...>>       -> <<pcpetname ...>>   (连字符误插)
3) <<plural-ize ...>>       -> <<pluralise ...>>   (连字符误插)
4) <<QUANTIFIER_OF_FOODS_CN ...>> -> 实现 widget
5) <<UPDATE_CLOTH_CN ...>>  -> 实现 widget
6) <<temple_rank>>          -> 实现 widget（翻译神殿等级）
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

WIDGETS = '''<<widget "QUANTIFIER_OF_FOODS_CN">><<set _cat to _args[0]>><<set _q to "份">><<if _cat is "drink">><<set _q to "杯">><<elseif _cat is "fruit">><<set _q to "个">><<elseif _cat is "vegetable">><<set _q to "份">><<elseif _cat is "meat">><<set _q to "块">><<elseif _cat is "dairy">><<set _q to "份">><<elseif _cat is "bakery">><<set _q to "个">><<elseif _cat is "sweet">><<set _q to "块">><<elseif _cat is "snack">><<set _q to "包">><<elseif _cat is "seafood">><<set _q to "份">><<elseif _cat is "egg">><<set _q to "个">><</if>><<print _q>><</widget>>
<<widget "UPDATE_CLOTH_CN">><<set _c to _args[0]>><<if _c is undefined or _c is "">><<print "衣物">><<else>><<set _n to (typeof _c is "object" ? (_c.cn_name_cap || _c.cn_name || _c.name) : _c)>><<print (_n || "衣物")>><</if>><</widget>>
<<widget "temple_rank">><<set _r to $temple_rank>><<if _r is "prospective">><<print "见习者">><<elseif _r is "initiate">><<print "教徒">><<elseif _r is "priest">><<print "司祭">><<elseif _r is "monk">><<print "修士">><<elseif _r is "nun">><<print "修女">><<else>><<print (_r || "信徒")>><</if>><</widget>>
'''


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    g = H.unescape(data)
    total = 0

    # 1) printNobody -> 无人
    for a, b in (("<<printNobody>>", "无人"),
                 (H.escape("<<printNobody>>", quote=False), "无人")):
        if a in data:
            n = data.count(a)
            data = data.replace(a, b)
            total += n
            print(f"  ✅ <<printNobody>> -> 无人  ({n})")
            break

    # 2) pcpet-name -> pcpetname
    for a, b in (("<<pcpet-name", "<<pcpetname"),
                 (H.escape("<<pcpet-name", quote=False), H.escape("<<pcpetname", quote=False))):
        if a in data:
            n = data.count(a)
            data = data.replace(a, b)
            total += n
            print(f"  ✅ <<pcpet-name -> <<pcpetname  ({n})")
            break

    # 3) plural-ize -> pluralise
    for a, b in (("<<plural-ize", "<<pluralise"),
                 (H.escape("<<plural-ize", quote=False), H.escape("<<pluralise", quote=False))):
        if a in data:
            n = data.count(a)
            data = data.replace(a, b)
            total += n
            print(f"  ✅ <<plural-ize -> <<pluralise  ({n})")
            break

    # 4-6) 实现 3 个 widget（插到 variablesStatic 末尾）
    VS_CLOSE = '&lt;&lt;/widget&gt;&gt;'
    vs = data.find('&lt;&lt;widget "variablesStatic"&gt;&gt;')
    if vs > 0:
        vc = data.find(VS_CLOSE, vs) + len(VS_CLOSE)
        data = data[:vc] + "\n" + H.escape(WIDGETS, quote=False) + data[vc:]
        total += 3
        print("  ✅ 已实现 QUANTIFIER_OF_FOODS_CN / UPDATE_CLOTH_CN / temple_rank")

    if total:
        open(HTML, "wb").write(data.encode("utf-8"))
        print(f"\n合计 {total} 处，写出 {HTML}")

    # 校验
    g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
    print("\n=== 校验 ===")
    for name in ["printNobody", "pcpet-name", "plural-ize"]:
        n = len(re.findall(r"<<" + re.escape(name) + r"\b", g2))
        print(f"  <<{name}>> 残留: {n}")
    for name in ["QUANTIFIER_OF_FOODS_CN", "UPDATE_CLOTH_CN", "temple_rank"]:
        nd = len(re.findall(r'<<widget "' + re.escape(name) + r'"', g2))
        nc = len(re.findall(r"<<" + re.escape(name) + r"\b", g2))
        print(f"  {name}: 定义 {nd} / 调用 {nc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
