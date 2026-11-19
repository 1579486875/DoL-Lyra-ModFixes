"""第 25-30 轮：综合验证（存档兼容 / 性能 / 结构 / JS 语法 / 模组描述 / 最终）。"""
import base64
import html
import io
import json
import os
import re
import subprocess
import tempfile
import zipfile
from collections import Counter

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
raw = z.read("assets/www/index.html")

print("=" * 94)
print("第 25 轮：存档兼容 —— 模组新增 $ 变量是否有兜底")
print("=" * 94)

g = html.unescape(raw.decode("utf-8", "replace"))
j = raw.find(b"[", raw.find(b"window.modDataValueZipList"))
k = raw.find(b"]", j)
parts = re.findall(r'"([A-Za-z0-9+/=\s]+)"', raw[j + 1:k].decode("utf-8", "replace"))

mods = []
for s in parts:
    b = base64.b64decode(re.sub(r"\s+", "", s))
    if b[:2] != b"PK":
        continue
    zz = zipfile.ZipFile(io.BytesIO(b))
    if "boot.json" not in zz.namelist():
        continue
    bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
    mods.append((bj.get("name") or "?", bj, zz))

game_vars = set(re.findall(r"\$([A-Za-z_][A-Za-z0-9_]{2,40})", g))
risky = 0
for name, bj, zz in mods:
    blob = ""
    for f in (bj.get("tweeFileList") or []) + (bj.get("scriptFileList") or []):
        try:
            blob += zz.read(f).decode("utf-8", "ignore") + "\n"
        except Exception:
            pass
    if not blob:
        continue
    used = Counter(re.findall(r"\$([A-Za-z_][A-Za-z0-9_]{2,40})", blob))
    own = {v for v in used if v not in game_vars and used[v] >= 3}
    for v in own:
        # 对象变量看子键兜底
        if re.search(r"\$" + v + r"\.[A-Za-z_]\w*\s+is\s+(?:not\s+)?undefined", blob):
            continue
        if re.search(r"\$" + v + r"\s+is\s+(?:not\s+)?undefined", blob):
            continue
        risky += 1
print(f"  疑似缺兜底的变量: {risky}（低于 5 视为正常，DoL 大量变量由 <<set>> 隐式初始化）")

print("\n" + "=" * 94)
print("第 26 轮：性能 —— index 体积与重复资源")
print("=" * 94)
infos = [(i.filename, i.file_size) for i in z.infolist() if i.file_size > 0]
infos.sort(key=lambda x: -x[1])
total = sum(s for _, s in infos)
print(f"  解压总量: {total/1048576:.1f} MB，文件 {len(infos)} 个")
print(f"  index.html: {len(raw)/1048576:.2f} MB")
print(f"  APK: {os.path.getsize(APK)/1048576:.2f} MB")

print("\n" + "=" * 94)
print("第 27 轮：结构 —— passage 配对 / 重名")
print("=" * 94)
gs = raw.decode("utf-8", "replace")
opens = len(re.findall(r"<tw-passagedata\b", gs))
closes = len(re.findall(r"</tw-passagedata>", gs))
names = [html.unescape(x) for x in re.findall(r'<tw-passagedata[^>]*name="([^"]+)"', gs)]
dup = {k2: v for k2, v in Counter(names).items() if v > 1}
print(f"  tw-passagedata: 开 {opens} / 闭 {closes}  {'✅' if opens == closes else '❌'}")
print(f"  重复 passage 名: {len(dup)}  {'✅' if not dup else '❌'}")

print("\n" + "=" * 94)
print("第 28 轮：JS 语法")
print("=" * 94)
tmp = os.path.join(tempfile.gettempdir(), "chk.js")
js_err = 0
js_files = 0
for name, bj, zz in mods:
    for f in bj.get("scriptFileList") or []:
        try:
            t = zz.read(f).decode("utf-8", "ignore")
        except Exception:
            continue
        js_files += 1
        open(tmp, "w", encoding="utf-8").write(t)
        r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if r.returncode != 0:
            js_err += 1
            print(f"  ❌ [{name}] {f}")
print(f"  检查 {js_files} 个 JS，语法错误 {js_err}  {'✅' if js_err == 0 else '❌'}")

print("\n" + "=" * 94)
print("第 29 轮：模组描述")
print("=" * 94)
no_nick = []
for name, bj, zz in mods:
    if not bj.get("nickName"):
        no_nick.append(name)
print(f"  缺 nickName 的模组: {len(no_nick)}")
for n in no_nick[:8]:
    print(f"    {n}")

print("\n" + "=" * 94)
print("第 30 轮：最终校验")
print("=" * 94)
checks = {
    "5 张映射表": all(('setup.' + t + ' to') in g for t in
                 ['NPCTypeList_cn_name', 'NPCNameList_cn_name', 'NPCTitleList_cn_name',
                  'majorAreas_cn_name', 'CafeFoodList_cn_name']),
    "bodyShapescn": "setup.bodyShapescn to" in g,
    "statDefaults 中文": 'name : "性欲"' in g,
    "faceVariantOptions 妆容": '"妆容": "makeup"' in g,
    "i18n 已烤入": g.count("的") > 100000,
    "Pub Avery 已翻译": "兰德里" in g,
}
for k2, v in checks.items():
    print(f"  {'✅' if v else '❌'} {k2}")

import hashlib
print(f"\n  大小  : {os.path.getsize(APK):,} 字节")
print(f"  SHA256: {hashlib.sha256(open(APK, 'rb').read()).hexdigest().upper()}")
print(f"  模组  : {len(parts)}")
