"""F53（第40轮）：10 个维度的综合扫描。"""
import html as H
import re
import zipfile
from collections import Counter

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
raw = zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace")
g = H.unescape(raw)
TICK = chr(96)


def has_cn(s):
    return bool(re.search(r"[\u4e00-\u9fff]", s))


def pure_en(s, minw=3):
    s = s.strip()
    if not s or has_cn(s):
        return False
    if len(re.findall(r"[A-Za-z]{2,}", s)) < minw:
        return False
    if re.search(r"[{}`\\]|=>|\bfunction\b|\bvar\b|\bconst\b|\blet\b|\breturn\b", s):
        return False
    return True


print("=" * 100)
print("40. <<option>> / <<listbox>> 里的整句英文")
print("=" * 100)
n = 0
for m in re.finditer(r'<<option\s+"([^"]{8,200})"', g):
    if pure_en(m.group(1)):
        n += 1
        if n <= 12:
            print(f"  {m.group(1)!r}")
print(f"  共 {n} 处")

print("\n" + "=" * 100)
print("41. 战斗动作名（<<actionsman>> 等 widget 里的）")
print("=" * 100)
for wname in ("actionsman", "actionsbeast", "actions", "actionstentacle"):
    m = re.search(r'<<widget "' + wname + r'">>(.*?)<</widget>>', g, re.S)
    if not m:
        continue
    body = m.group(1)
    ens = re.findall(r'"([A-Z][A-Za-z ]{5,40})"', body)
    ens = [e for e in ens if pure_en(e, 2)]
    if ens:
        print(f"  [{wname}] {len(ens)} 个英文: {ens[:8]}")

print("\n" + "=" * 100)
print("42. 物品/服装名（setup.clothes.* 里的 name）")
print("=" * 100)
n42 = 0
for m in re.finditer(r'cn_name\s*:\s*"([^"]{3,40})"', g):
    s = m.group(1)
    if pure_en(s, 1):
        n42 += 1
        if n42 <= 10:
            print(f"  {s!r}")
print(f"  共 {n42} 处（cn_name 里还是英文的）")

print("\n" + "=" * 100)
print("43. 技能名")
print("=" * 100)
m = re.search(r"setup\.skillsCN\s*=\s*\{(.*?)\};", g, re.S)
if m:
    pairs = re.findall(r'"?([A-Za-z_]+)"?\s*:\s*"([^"]*)"', m.group(1))
    print(f"  {len(pairs)} 项")
    bad = [(k, v) for k, v in pairs if pure_en(v, 1)]
    print(f"  英文残留 {len(bad)}: {bad[:8]}")
else:
    print("  未找到 setup.skillsCN")

print("\n" + "=" * 100)
print("44. 状态名（<<status>> / statNameCN）")
print("=" * 100)
for m in re.finditer(r"statNameCN\s*=\s*function", g):
    print(f"  找到 statNameCN @{m.start()}")

print("\n" + "=" * 100)
print("45. 成就名")
print("=" * 100)
m = re.search(r"setup\.feats\s*=\s*\{(.*?)\n\t\}", g, re.S)
if m:
    body = m.group(1)
    names = re.findall(r'name\s*:\s*"([^"]{3,60})"', body)
    bad = [x for x in names if pure_en(x, 2)]
    print(f"  {len(names)} 个成就，英文 {len(bad)}: {bad[:8]}")

print("\n" + "=" * 100)
print("46. 设置项标题（settingsHeader）")
print("=" * 100)
n46 = 0
for m in re.finditer(r'class="settingsHeader"[^>]*>([^<]{3,60})<', g):
    s = m.group(1).strip()
    if pure_en(s, 1):
        n46 += 1
        if n46 <= 10:
            print(f"  {s!r}")
print(f"  共 {n46} 处")

print("\n" + "=" * 100)
print("47. <<print>> 输出的纯英文字符串")
print("=" * 100)
n47 = 0
for m in re.finditer(r'<<print\s+"([^"]{8,120})"', g):
    if pure_en(m.group(1)):
        n47 += 1
        if n47 <= 10:
            print(f"  {m.group(1)!r}")
print(f"  共 {n47} 处")

print("\n" + "=" * 100)
print("48. either() 里的纯英文选项")
print("=" * 100)
n48 = 0
for m in re.finditer(r"either\(([^)]{10,600})\)", g):
    body = m.group(1)
    opts = re.findall(r'"([^"]{6,100})"', body)
    en = [o for o in opts if pure_en(o, 2)]
    if en and len(en) == len(opts):
        n48 += 1
        if n48 <= 8:
            print(f"  {en[:3]}")
print(f"  共 {n48} 处")

print("\n" + "=" * 100)
print("49. <<link>> 文本里的整句英文")
print("=" * 100)
n49 = 0
for m in re.finditer(r'<<link\s+\[\[\s*([^\]|]{8,120}?)\s*[|\]]', g):
    s = m.group(1).strip()
    if pure_en(s, 2):
        n49 += 1
        if n49 <= 12:
            print(f"  {s!r}")
print(f"  共 {n49} 处")

print("\n" + "=" * 100)
print("50. 汇总")
print("=" * 100)
print(f"  option 英文: {n}")
print(f"  cn_name 英文: {n42}")
print(f"  settingsHeader 英文: {n46}")
print(f"  print 英文: {n47}")
print(f"  either 全英文: {n48}")
print(f"  link 英文: {n49}")
