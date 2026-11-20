"""F03（第3轮）：<<link>> / <<goto>> / <<include>> / <<display>> 的 passage 目标存在性。"""
import html as H
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
raw = zipfile.ZipFile(APK).read("assets/www/index.html").decode("utf-8", "replace")

PASSAGES = {}
for m in re.finditer(r'<tw-passagedata[^>]*name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', raw, re.S):
    PASSAGES[m.group(1)] = H.unescape(m.group(2))

print(f"passage 总数: {len(PASSAGES)}")
names = set(PASSAGES)

# 1) <<link [[文本|目标]]>> 形式
print("\n" + "=" * 100)
print("1) <<link [[文本|目标]]>>")
print("=" * 100)
missing1 = []
n1 = 0
for pname, body in PASSAGES.items():
    for m in re.finditer(r'<<link\s+\[\[\s*([^\]|]*?)\s*\|\s*([^\]]+?)\s*\]\]', body):
        n1 += 1
        tgt = m.group(2).strip()
        if tgt in names:
            continue
        # 排除动态（含 $ _ << 等）
        if any(c in tgt for c in "$_<{}"):
            continue
        missing1.append((pname, tgt))

print(f"  链接总数 {n1}，缺失目标 {len(missing1)}")
by_target = {}
for pname, tgt in missing1:
    by_target.setdefault(tgt, []).append(pname)
for tgt, srcs in sorted(by_target.items(), key=lambda x: -len(x[1]))[:25]:
    print(f"    {tgt!r}  <- {len(srcs)} 处  ({srcs[:3]})")

# 2) <<goto "目标">>
print("\n" + "=" * 100)
print("2) <<goto>>")
print("=" * 100)
missing2 = []
n2 = 0
for pname, body in PASSAGES.items():
    for m in re.finditer(r'<<goto\s+"([^"]+)"', body):
        n2 += 1
        tgt = m.group(1)
        if tgt not in names:
            missing2.append((pname, tgt))
print(f"  总数 {n2}，缺失 {len(missing2)}")
for pname, tgt in missing2[:15]:
    print(f"    [{pname}] -> {tgt!r}")

# 3) <<include "目标">>
print("\n" + "=" * 100)
print("3) <<include>>")
print("=" * 100)
missing3 = []
n3 = 0
for pname, body in PASSAGES.items():
    for m in re.finditer(r'<<include\s+"([^"]+)"', body):
        n3 += 1
        if m.group(1) not in names:
            missing3.append((pname, m.group(1)))
print(f"  总数 {n3}，缺失 {len(missing3)}")

# 4) <<display "目标">>
print("\n" + "=" * 100)
print("4) <<display>>")
print("=" * 100)
missing4 = []
n4 = 0
for pname, body in PASSAGES.items():
    for m in re.finditer(r'<<display\s+"([^"]+)"', body):
        n4 += 1
        if m.group(1) not in names:
            missing4.append((pname, m.group(1)))
print(f"  总数 {n4}，缺失 {len(missing4)}")
for pname, tgt in missing4[:10]:
    print(f"    [{pname}] -> {tgt!r}")

# 5) 汇总
print("\n" + "=" * 100)
print("汇总")
print("=" * 100)
print(f"  <<link>> 缺失目标: {len(missing1)}")
print(f"  <<goto>> 缺失目标: {len(missing2)}")
print(f"  <<include>> 缺失:  {len(missing3)}")
print(f"  <<display>> 缺失:  {len(missing4)}")

with open(r"E:\TAML\_dol\work\_link_targets.txt", "w", encoding="utf-8") as f:
    f.write("=== link ===\n")
    for a, b in missing1:
        f.write(f"{a}\t{b}\n")
    f.write("=== goto ===\n")
    for a, b in missing2:
        f.write(f"{a}\t{b}\n")
    f.write("=== include ===\n")
    for a, b in missing3:
        f.write(f"{a}\t{b}\n")
    f.write("=== display ===\n")
    for a, b in missing4:
        f.write(f"{a}\t{b}\n")
print("\n已保存 _link_targets.txt")
