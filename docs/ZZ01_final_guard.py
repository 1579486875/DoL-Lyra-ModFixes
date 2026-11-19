"""第 4 轮：最终守卫 —— 在 TF01 之前跑，保证所有已知修复最终生效。

设计原则（模板 §3.1「自动让路」）：
  - 幂等：可以重复跑，结果一致
  - 只修「确定的 bug」，不做启发式猜测
  - 每项修复都有独立的计数与断言

覆盖的已知 bug：
  1. printNobody  -> 无人             (i18n 把 Nobody 当宏)
  2. flesh_text   -> flight_text      (flight 被翻成 flesh)
  3. pcpet-name   -> pcpetname        (连字符误插)
  4. plural-ize   -> pluralise        (连字符误插)
  5. ({'男':'m',...}) -> _bodyKeys    (JS 对象键被翻译)
  6. gender_body to _bodyTypes[_i].charAt(0) -> _bodyKeys[_i]
  7. compound.wraith to $compound -> $compoundWraith
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

FIXES = [
    ("1. printNobody",
     [("<<printNobody>>", "无人")],
     lambda g: g.count("<<printNobody>>") == 0),

    ("2. flesh_text",
     [("flesh_text", "flight_text")],
     lambda g: g.count("flesh_text") == 0),

    ("3. pcpet-name",
     [("<<pcpet-name", "<<pcpetname")],
     lambda g: g.count("<<pcpet-name") == 0),

    ("4. plural-ize",
     [("<<plural-ize", "<<pluralise")],
     lambda g: g.count("<<plural-ize") == 0),

    ("5. 中文键对象",
     [("({'男':'m','女':'f','中':'a'})", "_bodyKeys[_i]"),
      ('({\'男\':\'m\',\'女\':\'f\',\'中\':\'a\'})', "_bodyKeys[_i]"),
      ("{m:'m',f:'f',a:'a'}", "_bodyKeys[_i]")],
     lambda g: not re.search(r"\{\s*'?男'?\s*:", g)),

    ("6. gender_body 存值",
     [("gender_body to _bodyTypes[_i].charAt(0)", "gender_body to _bodyKeys[_i]")],
     lambda g: "gender_body to _bodyTypes[_i].charAt(0)" not in g),

    ("7. compoundWraith",
     [("<<if $compound>>\n\t\t\t<<set $compound.wraith to $compound>>\n\t\t<</if>>",
       "<<if $compoundWraith>>\n\t\t\t<<set $compound.wraith to $compoundWraith>>\n\t\t<</if>>")],
     lambda g: "<<set $compound.wraith to $compound>>" not in g),
]


def main():
    raw = open(HTML, "rb").read()
    data = raw.decode("utf-8", "replace")
    total = 0
    report = []

    for name, pairs, verify in FIXES:
        hit = 0
        for old, new in pairs:
            if not old:
                continue
            # 同时处理转义与原始形态
            for a, b in ((H.escape(old, quote=False), new), (old, new)):
                if a in data:
                    n = data.count(a)
                    data = data.replace(a, b)
                    hit += n
        total += hit
        g2 = H.unescape(data)
        ok = verify(g2)
        report.append((name, hit, ok))
        print(f"  {'✅' if ok else '❌'} {name:<26} 修 {hit:>3} 处  验证 {'通过' if ok else '失败'}")

    if total:
        open(HTML, "wb").write(data.encode("utf-8"))
        print(f"\n已写回 {HTML}  （共 {total} 处）")
    else:
        print("\n（无需修改，全部已就绪）")

    # 最终校验
    g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
    print("\n=== 最终校验 ===")
    checks = {
        "printNobody 残留": g.count("<<printNobody>>"),
        "flesh_text 残留": g.count("flesh_text"),
        "pcpet-name 残留": g.count("<<pcpet-name"),
        "plural-ize 残留": g.count("<<plural-ize"),
        "中文键对象残留": len(re.findall(r"\{\s*'?男'?\s*:", g)),
        "flight_text": g.count("flight_text"),
        "_bodyKeys": g.count("_bodyKeys"),
        "compoundWraith": g.count("compoundWraith"),
    }
    allok = True
    for k, v in checks.items():
        bad = k.endswith("残留")
        ok = (v == 0) if bad else (v > 0)
        if not ok:
            allok = False
        print(f"  {'✅' if ok else '❌'} {k}: {v}")

    print("\n" + ("✅ 最终守卫全部通过" if allok else "❌ 仍有残留，需人工处理"))
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
