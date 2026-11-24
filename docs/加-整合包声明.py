# -*- coding: utf-8 -*-
"""给 Lyra 模组加 NOTICE.md（整合包的总体声明）。"""
import base64
import io
import json
import re
import shutil
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"
DRY = "--write" not in sys.argv

NOTICE = """# 本整合包的声明与许可

> **本包不是 DoL 官方、汉化组官方或 Lyra 官方发布。**

## 一、游戏本体

**Degrees of Lewdity** — 作者 **Vrelnir**
- 博客：<https://vrelnir.blogspot.com>
- 源码：<https://gitgud.io/Vrelnir/degrees-of-lewdity>
- 许可：**CC BY-NC-SA 4.0**

## 二、中文汉化

**Degrees of Lewdity 中文本地化** — <https://github.com/Eltirosto/Degrees-of-Lewdity-Chinese-Localization>
- 许可：**CC BY-NC-SA 4.0**

汉化组要求：
> 游戏完全免费游玩，**严禁**将中文本地化版本**用作商业盈利用途**或**公开大肆传播**。
> 仅供交流学习，请于下载后 **24 小时内删除**。如果你未满 18 岁，请勿下载此游戏。

## 三、整合框架

**DoL-Lyra** — <https://github.com/DoL-Lyra/Lyra>
- 该仓库并非 DoL 或汉化组官方发布渠道
- 汉化组不为任何第三方整合包背书或担保

## 四、美术资源

**BEEESSS / BESC / 特写等**
- Degrees of Lewdity Graphics Mod — BEEESSS — <https://gitgud.io/BEEESSS/degrees-of-lewdity-graphics-mod>
- BEEESSS Community Sprite Compilation — Kaervek 等 — <https://gitgud.io/Kaervek/kaervek-beeesss-community-sprite-compilation>
- 完整作者名单见整合包 README 的 Credits 部分

## 五、模组

各模组版权归**各自作者**所有。

- **有明确许可的**：maplebirch（MIT）、FertilityExpansion（CC BY-NC-SA 4.0）
- **无显式声明的**（约 60 个）：按著作权法默认规则**保留所有权利**

本包**仅作个人使用与非商业分享**，不进行任何商业化。
**如任何模组作者提出异议，将立即移除对应内容。**

## 六、本包原创部分

以下内容由 **大赢经直插白皮赢道（1579486875）** 原创，采用 **CC BY-NC-SA 4.0**：

- **系统联动补全**（6 组系统联动）
- **美化修正**（贴图修正工具）
- 汉化修正与各类修复补丁

## 七、使用限制

1. **仅限 18 岁以上成年人使用**
2. **严禁任何形式的商业利用**
3. **不得公开大肆传播**
4. 建议下载后 **24 小时内删除**
5. 违反上述条款的后果由使用者自行承担

## 八、许可全文

- <https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hans>

---

*详细声明见 <https://github.com/1579486875/DoL-Lyra-ModFixes/blob/main/声明与许可.md>*
"""

raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)

target = None
for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1)):
    try:
        d = base64.b64decode(re.sub(r"\s+", "", s))
    except Exception:
        continue
    if d[:2] != b"PK":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(d))
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
    except Exception:
        continue
    if (bj.get("name") or "") == "Lyra":
        target = (s, zz, bj)
        break

if not target:
    print("❌ 未找到 Lyra 模组")
    sys.exit(1)

s_old, zz, bj = target
print("找到 Lyra 模组，现有文件:", zz.namelist())
print("boot.json:", json.dumps(bj, ensure_ascii=False))

# 改 boot.json
bj2 = dict(bj)
arr = bj2.get("additionFile")
if not isinstance(arr, list):
    arr = []
if "NOTICE.md" not in arr:
    arr.append("NOTICE.md")
bj2["additionFile"] = arr

# 重新打包
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zz.infolist():
        d = zz.read(info.filename)
        if info.filename == "boot.json":
            d = json.dumps(bj2, ensure_ascii=False, indent=2).encode("utf-8")
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, d)
    # 加 NOTICE.md
    zo.writestr("NOTICE.md", NOTICE.encode("utf-8"))

new_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
print("\n新 ZIP:", len(buf.getvalue()), "字节 → base64", len(new_b64), "字符")
print("原 base64:", len(s_old), "字符")

if DRY:
    print("[dry-run] 加 --write 写入")
    sys.exit(0)

# 备份
shutil.copy2(HTML, HTML + ".bak_before_notice")
print("已备份 index")

raw2 = raw.replace(s_old, new_b64, 1)
npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
if npass2 != npass:
    print("❌ passage 变化，中止")
    sys.exit(1)

# 校验数组条目数
m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw2, re.S)
n_before = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', m.group(1)))
n_after = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', m2.group(1)))
print("数组条目:", n_before, "->", n_after)
if n_before != n_after:
    print("❌ 条目数变化，中止")
    sys.exit(1)

open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
