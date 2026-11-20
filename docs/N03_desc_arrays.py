"""N03：查所有 _desc / _desc_CN 数组的对应关系，找 broad。"""
import html as H
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

print("=" * 95)
print("所有 _desc 数组 + 紧随的 _desc_CN")
print("=" * 95)
for m in re.finditer(r'<<set \$_desc to \[([^\]]+)\]>>', g):
    en = [x.strip().strip('"') for x in m.group(1).split(",")]
    # 找后面最近的 _desc_CN
    after = g[m.end():m.end() + 3000]
    m2 = re.search(r'<<set \$_desc_CN to \[([^\]]+)\]>>', after)
    cn = [x.strip().strip('"') for x in m2.group(1).split(",")] if m2 else []

    print(f"\n@{m.start()}")
    print(f"  EN 数组 {len(en)} 项")
    print(f"  CN 数组 {len(cn)} 项")
    if len(en) == len(cn):
        print(f"  ✅ 长度一致")
    else:
        print(f"  ❌ 长度不一致！差 {len(en) - len(cn)}")
        # 对齐看
        for i in range(max(len(en), len(cn))):
            e = en[i] if i < len(en) else "<none>"
            c = cn[i] if i < len(cn) else "<none>"
            print(f"    [{i}] {e!r} -> {c!r}")

    # 找 broad
    if "broad" in en:
        idx = en.index("broad")
        print(f"  ⚠️ broad 在索引 {idx}，对应 CN = {cn[idx] if idx < len(cn) else 'MISSING'!r}")

print("\n" + "=" * 95)
print("单独搜 broad 在任何数组里")
print("=" * 95)
for m in re.finditer(r'\bbroad\b', g):
    ctx = g[max(0, m.start() - 200):m.start() + 200]
    if re.search(r'\[[^\]]{0,500}"broad"', ctx) and "_desc" in ctx:
        print(f"  @{m.start()}: {ctx[:400]!r}\n")
