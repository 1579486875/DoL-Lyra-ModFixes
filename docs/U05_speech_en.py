"""U05：扫 $speech* 语音标记系统里的英文残留 + 修 speechrammalentrance。

这类残留的特点：
  它们在 <<if>> 的分支里，作为「动作副词」直接输出给玩家
  例：
    <<if $enemyarousal gte ...>>fencing
    <<elseif ...>>猛烈地
    <<else>>pressin
"""
import html as H
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

print("=" * 95)
print("1. ramming 的 2 处")
print("=" * 95)
for m in re.finditer(r"ramming", g):
    print(f"  @{m.start()}: {g[max(0,m.start()-200):m.start()+200]!r}\n")

print("=" * 95)
print("2. 正文里的「裸英文副词」（<<if>> 分支里只有英文单词）")
print("=" * 95)
# 形态：<<if ...>>\n  英文单词\n <<elseif/<<else/<</if>>
PAT = re.compile(r"<<(if|elseif|else)\b[^>]*>>\s*\n\s*([A-Za-z][A-Za-z\- ]{2,40})\s*\n\s*<<", re.M)
hits = []
for m in PAT.finditer(g):
    w = m.group(2).strip()
    if re.search(r"[\u4e00-\u9fff]", w):
        continue
    if len(re.findall(r"[A-Za-z]{2,}", w)) < 1:
        continue
    # 排除宏
    if w.startswith("<<") or w.startswith("<"):
        continue
    hits.append((m.start(), w, g[max(0, m.start() - 80):m.start() + 120]))

print(f"  共 {len(hits)} 处")
for pos, w, ctx in hits[:30]:
    print(f"    @{pos}  {w!r}")
    print(f"      {ctx!r}")

print("\n" + "=" * 95)
print("3. speechrammalentrance 的修法验证")
print("=" * 95)
print(f"  当前 'rammal' 出现: {g.count('rammal')}")
print(f"  'speechrammingentrance' 出现: {g.count('speechrammingentrance')}")
print(f"  'speechrammalentrance' 出现: {g.count('speechrammalentrance')}")
# 看同组变量 set 与 read 的比例
for kw in ("speechanusentrance", "speechvaginaentrance", "speechpenisentrance",
           "speechtribentrance", "speechmouthentrance", "speechfencingentrance"):
    s = len(re.findall(r"<<set\s+\$" + kw + r"\s+to", g))
    r = len(re.findall(r"\$" + kw, g))
    print(f"  ${kw}: set {s} / 总引用 {r}")
