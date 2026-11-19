"""DoL 整合包构建守门员（validate.py）

把历史上反复出问题的地方固化成自动检查。每次构建后跑一遍，任何一项 ❌ 就退出码 2。

检查项（对应历史事故）：
  1. widget 嵌套              —— 第 22 轮：variablesStatic 被截断
  2. widget 名含非 ASCII      —— 第 14 轮：characteristics -> ch一个racteristics
  3. 宏配对（if/for/switch/link/button/capture/widget/script）
  4. <<script>> 语法（Node）
  5. <<if>> 里的字符串比较值含中文 —— 翻译会破坏分支判断
  6. <<case>> 标签含中文      —— 同上
  7. setup.* 表的键被翻译     —— 会破坏索引
  8. passage 集合与 vanilla 一致
  9. 关键 setup 表存在
 10. 文件体积合理性
"""
import html
import os
import re
import subprocess
import sys
import tempfile
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VANILLA = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"
TMP_JS = os.path.join(tempfile.gettempdir(), "dsh_validate_check.js")

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    mark = "✅" if ok else "❌"
    line = f"  {mark} {name}"
    if detail:
        line += f"  —— {detail}"
    print(line)
    return ok


def main():
    if not os.path.exists(APK):
        print(f"❌ APK 不存在: {APK}")
        return 2

    z = zipfile.ZipFile(APK)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    g = html.unescape(raw)

    # 解析 passage
    passages = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        passages[html.unescape(m.group(1))] = html.unescape(m.group(2))

    print("=" * 90)
    print("1) widget 嵌套")
    print("=" * 90)
    nested = []
    for pn, b in passages.items():
        for m in re.finditer(r'<<widget\s+"([^"]+)"\s*>>(.*?)<</widget>>', b, re.S):
            if "<<widget" in m.group(2):
                nested.append((pn, m.group(1)))
    check("widget 无嵌套", not nested, f"{len(nested)} 处: {nested[:3]}")

    print("\n" + "=" * 90)
    print("2) widget 名含非 ASCII")
    print("=" * 90)
    names = re.findall(r'<<widget\s+"([^"]+)"', g)
    bad_names = [n for n in names if re.search(r"[^\x00-\x7f]", n)]
    check(f"widget 名全 ASCII（共 {len(names)} 个）", not bad_names, str(bad_names[:5]))

    print("\n" + "=" * 90)
    print("3) 宏配对")
    print("=" * 90)
    # 剥掉注释再做配对统计（注释里的宏不参与解析）
    clean_passages = {}
    for pn, b in passages.items():
        c = b
        for pat in (r"/\*.*?\*/", r"<!--.*?-->", r"/%.*?%/"):
            c = re.sub(pat, " ", c, flags=re.S)
        clean_passages[pn] = c

    PAIRS = [
        ("if", r"<<if\b", "<</if>>"),
        ("for", r"<<for\b", "<</for>>"),
        ("switch", r"<<switch\b", "<</switch>>"),
        ("link", r"<<link\b", "<</link>>"),
        ("button", r"<<button\b", "<</button>>"),
        ("capture", r"<<capture\b", "<</capture>>"),
        ("widget", r"<<widget\b", "<</widget>>"),
        ("script", r"<<script>>", "<</script>>"),
    ]
    all_ok = True
    for tag, op, cp in PAIRS:
        o = sum(len(re.findall(op, b)) for b in clean_passages.values())
        c = sum(b.count(cp) for b in clean_passages.values())
        ok = o == c
        all_ok &= ok
        check(f"<<{tag}>> {o}/{c}", ok, "" if ok else f"差 {o-c}")
    check("宏配对整体", all_ok)

    print("\n" + "=" * 90)
    print("4) <<script>> 语法（Node）")
    print("=" * 90)
    bad_scripts = []
    n_scripts = 0
    for pn, b in passages.items():
        for m in re.finditer(r"<<script>>(.*?)<</script>>", b, re.S):
            n_scripts += 1
            src = m.group(1)
            if not src.strip():
                continue
            open(TMP_JS, "w", encoding="utf-8").write(src)
            r = subprocess.run(["node", "--check", TMP_JS], capture_output=True,
                               text=True, encoding="utf-8", errors="replace")
            if r.returncode != 0:
                bad_scripts.append((pn, src[:80]))
    check(f"<<script>> 语法（{n_scripts} 块）", not bad_scripts,
          f"{len(bad_scripts)} 块出错: {bad_scripts[:2]}")

    print("\n" + "=" * 90)
    print("5) <<if>> 里字符串比较值含中文（翻译会破坏分支）")
    print("=" * 90)
    CJK = re.compile(r"[\u4e00-\u9fff]")
    # 只报「系统字段用了中文字面量」——那才会导致恒 false。
    # 形如 $xx.type is "中文" / xx.includes("中文")，其中 xx 是引擎/系统字段。
    SYSTEM_FIELDS = ("penisdesc", "precipitation", "fullDesc", "desc",
                     "type", "pronoun", "gender", "condom", "name")
    bad_cmp = []
    for pn, b in passages.items():
        for m in re.finditer(r'\$[\w$.\[\]]*\.(' + "|".join(SYSTEM_FIELDS) + r')\s*(?:is|isnot|===|!==)\s*"([^"]{1,40})"', b):
            field, val = m.group(1), m.group(2)
            if CJK.search(val):
                # 进一步确认：这个中文值是否真的出现在某处赋值里
                if f'"{val}"' in g:
                    continue  # 值也是中文 -> 自洽
                bad_cmp.append((pn, field, val))
    check("系统字段无孤立中文比较值", not bad_cmp,
          f"{len(bad_cmp)} 处: {bad_cmp[:3]}" if bad_cmp else "")

    print("\n" + "=" * 90)
    print("6) <<case>> 标签含中文")
    print("=" * 90)
    bad_case = []
    for pn, b in passages.items():
        for m in re.finditer(r"<<case\s+([^>\n]{1,60})>>", b):
            v = m.group(1).strip()
            if CJK.search(v) and not v.startswith('"'):
                bad_case.append((pn, v))
    check("<<case>> 无裸中文标签", not bad_case,
          f"{len(bad_case)} 处: {bad_case[:3]}" if bad_case else "")

    print("\n" + "=" * 90)
    print("7) setup.* 表的键被翻译")
    print("=" * 90)
    # 只检查「键是代码标识符」的表；faceStyleOptions/faceVariantOptions
    # 的键是给玩家看的显示名，本来就该是中文 —— 不检查。
    bad_tables = []
    for tname in ["NPCNameList", "loveInterestNpc"]:
        m = re.search(r"<<set setup\." + tname + r"\s+to\s*\[(.*?)\]", g, re.S)
        if not m:
            continue
        body = m.group(1)
        vals = re.findall(r'"([^"]+)"', body)
        cjk_vals = [v for v in vals if re.search(r"[\u4e00-\u9fff]", v)]
        if cjk_vals:
            bad_tables.append((tname, cjk_vals[:5]))
    check("标识符类 setup 数组未被误翻", not bad_tables, str(bad_tables[:3]))

    print("\n" + "=" * 90)
    print("8) passage 集合与 vanilla 一致")
    print("=" * 90)
    if os.path.exists(VANILLA):
        vz = zipfile.ZipFile(VANILLA)
        vraw = vz.read("assets/www/index.html").decode("utf-8", "replace")
        vp = set(html.unescape(m.group(1)) for m in
                 re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"', vraw))
        mp = set(passages.keys())
        check(f"passage 集合一致（{len(mp)} / {len(vp)}）", mp == vp,
              f"多出 {len(mp-vp)}，缺少 {len(vp-mp)}")
    else:
        check("passage 集合一致", False, "vanilla 包不存在，跳过")

    print("\n" + "=" * 90)
    print("9) 关键 setup 表存在")
    print("=" * 90)
    KEY_TABLES = ["NPCTypeList_cn_name", "NPCNameList_cn_name", "NPCTitleList_cn_name",
                  "majorAreas_cn_name", "CafeFoodList_cn_name", "bodyShapescn",
                  "faceVariantOptions", "faceStyleOptions"]
    missing = [t for t in KEY_TABLES if ("setup." + t + " to") not in g]
    check("关键 setup 表齐全", not missing, str(missing))

    print("\n" + "=" * 90)
    print("10) 文件体积")
    print("=" * 90)
    size_mb = os.path.getsize(APK) / 1048576
    ok_size = 150 <= size_mb <= 250
    check(f"APK 体积 {size_mb:.2f} MB（合理区间 150-250）", ok_size)

    # 汇总
    print("\n" + "=" * 90)
    failed = [r for r in results if not r[1]]
    print(f"结果：{len(results) - len(failed)} / {len(results)} 通过")
    if failed:
        print("\n❌ 失败项：")
        for name, _, detail in failed:
            print(f"   {name}  {detail}")
        return 2
    print("✅ 全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
