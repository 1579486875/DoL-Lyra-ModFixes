"""Q05：查 relation-box 里 NPC_CN_NAME 的所有错误形态。"""
import html as H
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

print("=" * 95)
print("1. relation-box 完整内容（前 4500 字）")
print("=" * 95)
m = re.search(r'<<widget "relation-box">>(.*?)<</widget>>', g, re.S)
wb = m.group(1) if m else ""
print(wb[:4500])

print("\n" + "=" * 95)
print("2. 所有 NPC_CN_NAME 的错误形态（宏嵌套 / 多余的 >>>）")
print("=" * 95)
for mm in re.finditer(r"<<NPC_CN_NAME[^>]*>>>>", g):
    print(f"  @{mm.start()}: {g[max(0,mm.start()-120):mm.start()+180]!r}\n")

print("\n" + "=" * 95)
print("3. 统计各种形态")
print("=" * 95)
pats = {
    "<<if (<<NPC_CN_NAME ...>>>>>": len(re.findall(r"<<if \(<<NPC_CN_NAME", g)),
    "<<if <<NPC_CN_NAME ...>>>>>": len(re.findall(r"<<if <<NPC_CN_NAME", g)),
    "显示处 <<NPC_CN_NAME ...>>>>>>": len(re.findall(r"<<NPC_CN_NAME [^>]*>>>>>>", g)),
    "正常 setup.NPC_CN_NAME(": g.count("setup.NPC_CN_NAME("),
}
for k, v in pats.items():
    print(f"  {v:>4}  {k}")
