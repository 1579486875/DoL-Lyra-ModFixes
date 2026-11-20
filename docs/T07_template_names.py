"""T07：查 Template.add 的模板名被翻译的情况 + chatter1 未翻（转义）原因。"""
import html as H
import re

g = H.unescape(open(r"E:\TAML\_dol\work\index_modded6.html", "rb").read().decode("utf-8", "replace"))

print("=" * 95)
print("1. 所有 Template.add 的名字")
print("=" * 95)
names = re.findall(r'Template\.add\(\s*"([^"]+)"', g)
print(f"共 {len(names)} 个")
cn_names = []
for n in names:
    has_cn = bool(re.search(r"[\u4e00-\u9fff]", n))
    mark = "❌" if has_cn else "  "
    print(f"  {mark} {n!r}")
    if has_cn:
        cn_names.append(n)

print("\n" + "=" * 95)
print(f"2. 名字含中文的: {len(cn_names)}")
print("=" * 95)
for n in cn_names:
    print(f"  ❌ {n!r}")

# 对照基线的模板名清单
GOOD = r"E:\TAML\_dol\archive\DoL-Lyra-0.5.12.13-CHS-modded_20261120-061313_修复arsc可安装.apk"
import zipfile
gb = H.unescape(zipfile.ZipFile(GOOD).read("assets/www/index.html").decode("utf-8", "replace"))
base_names = re.findall(r'Template\.add\(\s*"([^"]+)"', gb)
print("\n" + "=" * 95)
print(f"3. 基线模板名清单（{len(base_names)} 个）")
print("=" * 95)
for n in base_names:
    print(f"  {n!r}")

print("\n" + "=" * 95)
print("4. chatter1 的实际内容（看转义）")
print("=" * 95)
m = re.search(r'Template\.add\(\s*"chatter1"\s*,\s*(.{0,900})', g, re.S)
if m:
    print(repr(m.group(1)[:850]))
