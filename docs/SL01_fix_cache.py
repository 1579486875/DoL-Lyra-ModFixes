"""修复 setup.NPC_CN_* 的缓存问题 + a light / You have。

问题：LB01 里的 typeTable()/nameTable() 用了缓存变量：
    if (typeMap === null) typeMap = parseTable(st.NPCTypeList_cn_name);
第一次调用时如果表还没定义 -> typeMap = {} -> 永远返回英文。

修法：去掉缓存，每次实时读。
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    total = 0

    # ---- 1) 替换 LB01 的带缓存版本 ----
    OLD_CACHE = '''    var typeMap = null, nameMap = null;

    function typeTable() {
        if (typeMap === null) typeMap = parseTable(st.NPCTypeList_cn_name);
        return typeMap;
    }
    function nameTable() {
        if (nameMap === null) nameMap = parseTable(st.NPCNameList_cn_name);
        return nameMap;
    }'''

    NEW_CACHE = '''    /* 不缓存：NPCTypeList_cn_name 可能在 script 执行后才定义 */
    function typeTable() {
        return parseTable(st.NPCTypeList_cn_name);
    }
    function nameTable() {
        return parseTable(st.NPCNameList_cn_name);
    }'''

    for a, b in ((H.escape(OLD_CACHE, quote=False), H.escape(NEW_CACHE, quote=False)),
                 (OLD_CACHE, NEW_CACHE)):
        if a in data:
            data = data.replace(a, b, 1)
            total += 1
            print("  ✅ 去掉 typeTable/nameTable 缓存")
            break
    else:
        print("  ⚠️ 未找到缓存片段，尝试变体")
        # 变体：可能缩进不同
        pat = re.compile(r"var typeMap = null, nameMap = null;\s*\n\s*\n\s*function typeTable\(\) \{\s*\n\s*if \(typeMap === null\) typeMap = parseTable\(st\.NPCTypeList_cn_name\);\s*\n\s*return typeMap;\s*\n\s*\}\s*\n\s*function nameTable\(\) \{\s*\n\s*if \(nameMap === null\) nameMap = parseTable\(st\.NPCNameList_cn_name\);\s*\n\s*return nameMap;\s*\n\s*\}")
        if pat.search(data):
            data = pat.sub(H.escape(NEW_CACHE, quote=False), data, 1)
            total += 1
            print("  ✅ 去掉缓存（正则变体）")

    # ---- 2) a light / You have ----
    PAIRS = [
        ("你有着 a light 的皮肤", "你有着 浅色 的皮肤"),
        ("你有着 a dark 的皮肤", "你有着 深色 的皮肤"),
        ("你有着 a tan 的皮肤", "你有着 古铜色 的皮肤"),
        ("You have 一个阴道", "你有一个阴道"),
        ("You have 一个阴茎", "你有一个阴茎"),
    ]
    for old, new in PAIRS:
        for a, b in ((H.escape(old, quote=False), H.escape(new, quote=False)), (old, new)):
            if a in data:
                n = data.count(a)
                data = data.replace(a, b)
                total += n
                print(f"  ✅ {old!r} -> {new!r} ({n})")
                break

    # ---- 3) 「a light」这种裸英文片段的通用清理 ----
    # 形如 "有 a light 的" / "有 a dark 的"
    GENERIC = [
        (r"有 a light 的", "有 浅色 的"),
        (r"有 a dark 的", "有 深色 的"),
        (r"有 a tan 的", "有 古铜色 的"),
        (r"有 a pale 的", "有 苍白 的"),
    ]
    for pat_s, rep in GENERIC:
        n = len(re.findall(pat_s, data))
        if n:
            data = re.sub(pat_s, rep, data)
            total += n
            print(f"  ✅ 通用清理 {pat_s!r} ({n})")

    print(f"\n合计 {total} 处")
    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")

    # 校验
    g = H.unescape(data)
    print("\n=== 校验 ===")
    print(f"  'a light' 残留: {g.count('a light')}")
    print(f"  'You have' 残留: {g.count('You have')}")
    print(f"  缓存变量 typeMap: {'var typeMap = null' in g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
