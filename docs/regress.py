"""历史问题全量回归 + 同类扩散扫描（regress.py）

分两部分：
  A) 29 个历史事故逐项断言（是否复发）
  B) 对每类事故做「同类扩散扫描」（拔出萝卜带出泥）

用法：python regress.py
退出码 0 = 全部通过；2 = 有复发或新发现
"""
import html
import re
import sys
import zipfile
from collections import Counter, defaultdict

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"
CJK = re.compile(r"[\u4e00-\u9fff]")

fails = []
notes = []


def ok(name, detail=""):
    print(f"  ✅ {name}")


def bad(name, detail=""):
    fails.append((name, detail))
    print(f"  ❌ {name}  {detail}")


def main():
    z = zipfile.ZipFile(APK)
    raw = z.read("assets/www/index.html").decode("utf-8", "replace")
    g = html.unescape(raw)

    vz = zipfile.ZipFile(VAN)
    vg = html.unescape(vz.read("assets/www/index.html").decode("utf-8", "replace"))

    passages = {}
    for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]+)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
        b = html.unescape(m.group(2))
        c = b
        for pat in (r"/\*.*?\*/", r"<!--.*?-->", r"/%.*?%/"):
            c = re.sub(pat, " ", c, flags=re.S)
        passages[html.unescape(m.group(1))] = (b, c)

    print("=" * 92)
    print("A) 历史事故逐项断言")
    print("=" * 92)

    # 1-3 NPC 宏
    for macro in ("NPC_CN_NAME", "NPC_CN_TYPE", "BODYPARTS_CN_NAME"):
        if macro == "BODYPARTS_CN_NAME":
            v = "st.BODYPARTS_CN_NAME =" in g
        else:
            v = (f'<<widget "{macro}">>' in g) or (f"st.{macro} =" in g)
        (ok if v else bad)(f"[1-3] {macro} 已定义")

    # 4 嵌套宏（relation-box 事故）
    n = len(re.findall(r"NPC_CN_NAME\s+<<NPC_CN_NAME", g))
    (ok if n == 0 else bad)(f"[4] NPC_CN_NAME 无嵌套", f"{n} 处")

    # 5 cheats-npcs 的 NPCNameList 兜底
    v = "(setup.NPCNameList || $NPCNameList || [])" in g
    (ok if v else bad)("[5] cheats-npcs 有 NPCNameList 兜底")

    # 6 单单词 UI 已翻
    miss = [w for w in ("怪物女孩", "怪物男孩", "野兽", "测试") if w not in g]
    (ok if not miss else bad)("[6] 单单词 UI 已翻译", str(miss))

    # 7 faceVariantOptions 键数 == _faceVariantscn 动态
    v = "Object.keys(setup.faceVariantOptions[V.facestyle])" in g
    (ok if v else bad)("[7] faceVariant 用 Object.keys 动态配对")

    # 8 widget 名全 ASCII
    names = re.findall(r'<<widget\s+"([^"]+)"', g)
    badn = [x for x in names if re.search(r"[^\x00-\x7f]", x)]
    (ok if not badn else bad)(f"[8] widget 名全 ASCII（{len(names)}）", str(badn[:3]))

    # 9 either() 全角逗号 —— 按括号配平提取，不受内嵌宏影响
    n = 0
    samples = []
    pos = 0
    while True:
        k = g.find("either(", pos)
        if k < 0:
            break
        pos = k + 1
        # 前面必须是 << 开头（说明在宏里）
        head = g[max(0, k - 40):k]
        if "<<" not in head:
            continue
        i2 = k + len("either(")
        d2 = 1
        in_dq = False
        in_sq = False
        esc = False
        while i2 < len(g) and d2 > 0:
            ch = g[i2]
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif in_dq:
                if ch == '"':
                    in_dq = False
            elif in_sq:
                if ch == "'":
                    in_sq = False
            elif ch == '"':
                in_dq = True
            elif ch == "'":
                in_sq = True
            elif ch == "(":
                d2 += 1
            elif ch == ")":
                d2 -= 1
            i2 += 1
        inner = g[k + len("either("):i2 - 1]
        base = re.sub(r'"(?:[^"\\]|\\.)*"', '""', inner)
        base = re.sub(r"'(?:[^'\\]|\\.)*'", "''", base)
        base = re.sub(r"`(?:[^`\\]|\\.)*`", "``", base)
        if "，" in base:
            n += 1
            if len(samples) < 3:
                samples.append(inner[:80])
    (ok if n == 0 else bad)("[9] either() 参数无全角逗号", f"{n} 处: {samples}")

    # 10 _speechWraith 拼接
    sw = re.findall(r"<<set\s+_speechWraith\s+to\s+([^>]{1,200})>>", g)
    lit = [s for s in sw if "_line1" in s and "+" not in s]
    (ok if not lit else bad)("[10] _speechWraith 是拼接不是字面量", str(lit[:2]))

    # 11 孤立 */
    stray = 0
    for pn, (b, c) in passages.items():
        if c.count("*/") > c.count("/*"):
            stray += 1
    (ok if stray == 0 else bad)("[11] 无孤立 */", f"{stray} 个 passage")

    # 12 含 & 的 passage 名已反转义
    amp = [pn for pn in passages if "&amp;" in pn]
    (ok if not amp else bad)("[12] passage 名已反转义", str(amp[:3]))

    # 13 状态名
    miss = [x for x in ("疼痛：", "性奋：", "疲劳：", "压力：", "创伤：", "自控：", "诱惑：")
            if x not in g]
    (ok if not miss else bad)("[13] 7 个状态名已中文", str(miss))

    # 14 区块标题
    miss = []
    for t in ("Body", "Head", "Personality"):
        if re.search(r'&lt;div class="settingsHeader[^"]*"&gt;\s*' + t + r'\s*&lt;/div&gt;', raw):
            miss.append(t)
    (ok if not miss else bad)("[14] Body/Head/Personality 已中文", str(miss))

    # 15 仪态列表
    v = ('"妆容": "makeup"' in g) and ('"Makeup"' not in g)
    (ok if v else bad)("[15] 仪态含妆容且无 Makeup")

    # 16 description_CN
    (ok if "st.description_CN = descCN" in g else bad)("[16] setup.description_CN 已定义")

    # 17 wTimerProgress
    (ok if re.search(r'<<widget "wTimerProgress"', g) else bad)("[17] wTimerProgress 已定义")

    # 18 widget 嵌套
    nested = sum(1 for m in re.finditer(r'<<widget\s+"([^"]+)"\s*>>(.*?)<</widget>>', g, re.S)
                 if "<<widget" in m.group(2))
    (ok if nested == 0 else bad)("[18] widget 无嵌套", f"{nested} 处")

    # 19 bus 缺 to
    n = len(re.findall(r'<<set\s+\$bus\s+"', g))
    (ok if n == 0 else bad)("[19] <<set $bus 有 to", f"{n} 处")

    # 20 typeTable 无缓存
    (ok if "var typeMap = null" not in g else bad)("[20] typeTable 无缓存")

    # 21 $obj.中文属性
    hit = set()
    for m in re.finditer(r"\$(\w+)\.([\u4e00-\u9fff]+)(?=[\s\]\)\>,|&;.]|$)", g):
        hit.add(f"${m.group(1)}.{m.group(2)}")
    (ok if not hit else bad)("[21] 无 $obj.中文属性", str(sorted(hit)[:3]))

    # 22 penisdesc 中英兼容
    v = 'includes("马")' in g and 'includes("horse")' in g
    (ok if v else bad)("[22] penisdesc 中英兼容")

    # 23 Black Wolf 数组
    (ok if '"Black Wolf"' in g else bad)("[23] Black Wolf 数组正确")

    # 24 Weather 数组
    n = len(re.findall(r'\["下雨",\s*"下雪"\]', g))
    (ok if n == 0 else bad)("[24] Weather 数组无中文", f"{n} 处")

    # 25 displayName
    allDn = re.findall(r'displayName:\s*"([^"]{1,60})"', g)
    en = [x for x in allDn if not CJK.search(x)]
    (ok if not en else bad)("[25] displayName 无纯英文", str(en[:3]))

    # 26 面部风格 undefined
    v = "setup.bodyShapescn" in g
    (ok if v else bad)("[26] bodyShapescn 存在")

    # 27 关系值名
    v = "relation-box" in g or "relationbox" in g.lower()
    (ok if v else bad)("[27] relation-box 存在")

    # 28 7 个 setup 函数
    miss = [f for f in ("BODYPARTS_CN_NAME", "CAFE_FOOD_CN", "DirectionCN",
                        "NPC_CN_TOOLNAME", "brothelshowType_CN", "update_cloth_cn")
            if f"st.{f} =" not in g]
    (ok if not miss else bad)("[28] 6 个 setup 函数齐全", str(miss))

    # 29 setup.T
    (ok if "st.T.npcClothesItems" in g else bad)("[29] setup.T 容器存在")

    # ============ B) 同类扩散扫描 ============
    print("\n" + "=" * 92)
    print("B) 同类扩散扫描")
    print("=" * 92)

    # B1: setup.<中文> / _<中文> 属性
    print("\n[B1] setup./_ 级中文属性")
    hits = set()
    for m in re.finditer(r"\b(setup|_\w+)\.([\u4e00-\u9fff]+)(?=[\s\]\)\>,|&;.]|$)", g):
        hits.add(f"{m.group(1)}.{m.group(2)}")
    if hits:
        print(f"  ❌ {len(hits)} 个: {sorted(hits)[:8]}")
        fails.append(("[B1] setup./_ 中文属性", str(sorted(hits)[:5])))
    else:
        print("  ✅ 0 个")

    # B2: 中文变量名
    print("\n[B2] 中文变量名")
    hits = set(re.findall(r"\$([\u4e00-\u9fff][\w\u4e00-\u9fff]*)", g))
    if hits:
        print(f"  ⚠️ {len(hits)} 个: {sorted(hits)[:8]}")
        notes.append(("[B2] 中文变量名", str(sorted(hits)[:5])))
    else:
        print("  ✅ 0 个")

    # B3: 文本字段英文 === 判断，但该字段的值在 modded 里是中文
    print("\n[B3] 文本字段英文 === 判断（值可能已中文）")
    risky = []
    for m in re.finditer(r"\.([\w]+)\s*(?:is|===)\s*\"([A-Za-z][\w -]{2,25})\"", g):
        field, val = m.group(1), m.group(2)
        # 该英文字面量在 modded 里除判断外是否还出现
        cnt = g.count(f'"{val}"')
        if cnt <= 1:
            risky.append((field, val))
    uniq = sorted(set(risky))
    if uniq:
        print(f"  ⚠️ {len(uniq)} 种（需逐个判断）")
        for f, v in uniq[:15]:
            print(f"    .{f} === {v!r}  （全文仅 {g.count(chr(34)+v+chr(34))} 次）")
        notes.append(("[B3] 疑似失效的英文判断", str(uniq[:5])))
    else:
        print("  ✅ 0 种")

    # B4: JS 配置对象里的英文字面量（displayName/textMap/options）
    print("\n[B4] JS 配置对象英文字面量")
    js = []
    for key in ("displayName", "textMap", "options", "strings"):
        for m in re.finditer(key + r':\s*["\']([A-Za-z][^"\']{2,40})["\']', g):
            js.append((key, m.group(1)))
    if js:
        print(f"  ⚠️ {len(js)} 处")
        for k, v in js[:10]:
            print(f"    {k}: {v!r}")
        notes.append(("[B4] JS 配置英文", str(js[:5])))
    else:
        print("  ✅ 0 处")

    # B5: widget 里硬编码的纯英文标签行（形如 \n\t\tEnglish:\n）
    print("\n[B5] widget 里硬编码英文标签")
    label = re.compile(r"\n[ \t]+([A-Z][A-Za-z ]{2,25}):[ \t]*\n")
    found = []
    for m in label.finditer(g):
        w = m.group(1)
        if w in ("http", "https", "file", "data"):
            continue
        found.append(w)
    c = Counter(found)
    if c:
        print(f"  ⚠️ {len(c)} 种")
        for w, n in c.most_common(15):
            print(f"    {w!r} × {n}")
        notes.append(("[B5] 硬编码英文标签", str(c.most_common(5))))
    else:
        print("  ✅ 0 种")

    # B6: <<case "英文">> 但 switch 的变量被赋值为中文
    print("\n[B6] <<case>> 中英混用")
    bad_case = []
    for m in re.finditer(r'<<switch\s+\$(\w+)>>(.*?)<</switch>>', g, re.S):
        var, body = m.group(1), m.group(2)
        cases = set(re.findall(r'<<case\s+"([^"]+)"', body))
        # 该变量被赋值的值
        assigns = set(re.findall(r"\$" + var + r"\s+(?:to|is)\s+\"([^\"]+)\"", g))
        if cases and assigns:
            if all(CJK.search(x) for x in cases) and all(not CJK.search(x) for x in assigns):
                bad_case.append((var, sorted(cases)[:3], sorted(assigns)[:3]))
    if bad_case:
        print(f"  ❌ {len(bad_case)} 组")
        for v, c_, a in bad_case[:5]:
            print(f"    ${v}: case={c_}  赋值={a}")
        fails.append(("[B6] case/赋值中英不一致", str(bad_case[:3])))
    else:
        print("  ✅ 0 组")

    # 汇总
    print("\n" + "=" * 92)
    print(f"结果：失败 {len(fails)}，需人工确认 {len(notes)}")
    print("=" * 92)
    if fails:
        print("\n❌ 复发 / 新发现：")
        for n, d in fails:
            print(f"   {n}  {d}")
    if notes:
        print("\n⚠️ 需人工确认：")
        for n, d in notes:
            print(f"   {n}  {d}")
    return 0 if not fails else 2


if __name__ == "__main__":
    sys.exit(main())
