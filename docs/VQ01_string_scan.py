"""第 28-32 轮：系统扫描「字段值被中文化，但代码仍判断英文子串」的地方。

方法：
  1. 收集所有 xxx.includes("英文") / xxx is "英文" 的判断
  2. 对每个英文串，看它在 modded 的 _pd/_desc 等取值数组里是否已被中文替换
  3. 输出「英文串在 modded 里 0 次出现，但仍在被判断」的清单
"""
import html
import re
import zipfile
from collections import Counter

MOD = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"
CJK = re.compile(r"[\u4e00-\u9fff]")


def load(p):
    z = zipfile.ZipFile(p)
    return html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))


mg = load(MOD)
vg = load(VAN)

print("=" * 94)
print("1) 收集所有 .includes(\"...\") 的英文参数")
print("=" * 94)
m_inc = Counter()
v_inc = Counter()
for g, c in ((mg, m_inc), (vg, v_inc)):
    for m in re.finditer(r'\.\s*includes\(\s*["\']([A-Za-z][\w -]{2,30})["\']\s*\)', g):
        c[m.group(1)] += 1

print(f"  modded {len(m_inc)} 种，vanilla {len(v_inc)} 种")

print("\n" + "=" * 94)
print("2) vanilla 有、modded 没有的英文判断（可能被中文化后失效）")
print("=" * 94)
lost = sorted(set(v_inc) - set(m_inc))
print(f"  {len(lost)} 种")
for x in lost:
    # 这个词在 modded 里还出现吗
    n = mg.count(x)
    print(f"    {x!r:<28} vanilla {v_inc[x]:>2} 次  |  modded 全文 {n:>4} 次")

print("\n" + "=" * 94)
print("3) 两边都有，但 modded 里这个词仅出现在判断里（值已中文化）")
print("=" * 94)
risky = []
for x in sorted(set(v_inc) & set(m_inc)):
    n_m = mg.count(x)
    n_judge = m_inc[x]
    if n_m <= n_judge:  # 除了判断处，别处都没出现 -> 值是中文
        risky.append((x, m_inc[x], n_m))
print(f"  {len(risky)} 种")
for x, j, n in risky[:30]:
    print(f"    {x!r:<28} 判断 {j} 次  全文仅 {n} 次")

print("\n" + "=" * 94)
print("4) 检查关键字段的中文化情况")
print("=" * 94)
FIELDS = ["genitals.name", "genitals.type", "clothes.lower.name", "clothes.upper.name",
          "worn.genitals.name", "worn.upper.type", "worn.lower.type", "npc.type",
          "penisdesc", "description"]
for f in FIELDS:
    # 该字段的比较值
    pats = set()
    for m in re.finditer(re.escape(f) + r'\s*(?:is|===)\s*["\']([^"\']{1,30})["\']', mg):
        pats.add(m.group(1))
    cjk_vals = [p for p in pats if CJK.search(p)]
    eng_vals = [p for p in pats if not CJK.search(p)]
    if cjk_vals:
        print(f"\n  {f}: 中文比较 {len(cjk_vals)} 英文比较 {len(eng_vals)}")
        print(f"    中文示例: {cjk_vals[:5]}")
        print(f"    英文示例: {eng_vals[:5]}")
