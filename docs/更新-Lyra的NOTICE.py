# -*- coding: utf-8 -*-
"""把整合后的声明写进 Lyra 模组的 NOTICE.md。"""
import base64
import io
import json
import re
import sys
import zipfile

HTML = r"E:\TAML\_dol\work\index_modded6.html"

NOTICE = """# 本整合包的声明与许可

> **本包是一个非商业的个人整合包，不是 DoL 官方、汉化组官方或 Lyra 官方发布。**

## 一、游戏本体

**Degrees of Lewdity** — 作者 **Vrelnir**
- 博客：<https://vrelnir.blogspot.com>
- 源码：<https://gitgud.io/Vrelnir/degrees-of-lewdity>
- **许可：CC BY-NC-SA 4.0**

## 二、中文汉化

**Degrees of Lewdity 中文本地化** — **Eltirosto / 汉化组**
- <https://github.com/Eltirosto/Degrees-of-Lewdity-Chinese-Localization>
- **许可：CC BY-NC-SA 4.0**

汉化组要求：
> 游戏完全免费游玩，**严禁**将中文本地化版本**用作商业盈利用途**或**公开大肆传播**。
> 仅供交流学习，请于下载后 **24 小时内删除**。如果你未满 18 岁，请勿下载此游戏。

汉化组明确**不为任何第三方整合包背书或担保**。

## 三、整合框架

**DoL-Lyra** — <https://github.com/DoL-Lyra/Lyra>
- 该仓库并非 DoL 或汉化组官方发布渠道

## 四、美术资源

**BEEESSS / BESC / 特写等**
- Degrees of Lewdity Graphics Mod — **BEEESSS** — <https://gitgud.io/BEEESSS/degrees-of-lewdity-graphics-mod>
- BEEESSS Community Sprite Compilation — Kaervek 等 — <https://gitgud.io/Kaervek/kaervek-beeesss-community-sprite-compilation>

完整作者名单见整合包 README 的 Credits 部分。

## 五、模组作者（版权归各自作者）

### 明确开源许可

| 模组 | 作者 | 许可 |
|---|---|---|
| maplebirch / MapleBirchCE | 枫桦叶 | MIT + CC BY-NC-SA 4.0 |
| FertilityExpansion | Liliths-Legacy | CC BY-NC-SA 4.0 |
| CombatSkills / CombatActionsExt / LocationsExt | **1KMJTIO194** | **MIT**（见各模组内 LICENSE + NOTICE） |
| ModI18N 等 5 个 | Eltirosto / 汉化组 | CC BY-NC-SA 4.0 |

### 仅限非商业

作者 **𝑁𝐸𝐸𝐷𝑀𝐸𝐸𝑇 遇欲**（<https://github.com/ANLINSTUDIO>）：
美化修正 / SmartPhone Alpha / 小小PC / 露出拓展

### 无显式声明（默认保留所有权利）

| 模组 | 作者 |
|---|---|
| BasicNeeds | YanYeQi |
| DoLSims | 丧心（MissedHeart） |
| DomRobin | 零环零理想 & Robin's GF & 枫桦叶 |
| 猫咖出租屋 | Maomao & 七 |
| NPC Avatars Mod | Eudemonism00 |
| clothesicon | KonoLLo |
| More Love Interests Mod | 苯环（Nephthelana） |
| timemulti | L |
| GuideToMe | Ayndpa |
| Wraith'sReflection | 水墨儿（悠飘过去了） |
| PCBakery | Liliths-Legacy |
| more useful foodstuff / HonestMarkets | 隨風飄逸 |
| ModdedClothesAddon | suin14 |
| ModLoader 全家桶 | Lyoko-Jeremie |
| Lyra / Cheat-Lyra / CombatStatusDisplay-Lyra | DoL-Lyra |
| Clothes | ⚠️ 来源不明 |

**本包仅作个人使用与非商业分享。如任何作者提出异议，将立即移除对应内容。**

## 六、本包原创（大赢经直插白皮赢道）

采用 **CC BY-NC-SA 4.0**：

- **系统联动补全**（6 组系统联动）
- **兼容/修复类 13 个**：Toilet Addon / Cheat Face Fix / Dead Link Stubs /
  Game Dead Link Stubs / EffectsMan Null Guard / Face Variant Fill / Handheld Idle Fix /
  Icon Path Fix / Missing Widget Stubs / Part Type Guard / Settings Null Guard /
  Npc Name CN / Stat Name CN
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

*完整声明：<https://github.com/1579486875/DoL-Lyra-ModFixes/blob/main/声明与许可.md>*
"""

raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
mm = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)

target = None
for s in re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', mm.group(1)):
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
    print("❌ 未找到 Lyra")
    sys.exit(1)

s_old, zz, bj = target
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
    written = False
    for info in zz.infolist():
        d = zz.read(info.filename)
        if info.filename == "NOTICE.md":
            d = NOTICE.encode("utf-8")
            written = True
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        zi.external_attr = info.external_attr
        zo.writestr(zi, d)
    if not written:
        zo.writestr("NOTICE.md", NOTICE.encode("utf-8"))

new_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
raw2 = raw.replace(s_old, new_b64, 1)

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw2, re.S)
n_b = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', mm.group(1)))
n_a = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', m2.group(1)))
print("passage:", npass, "->", npass2, "| 条目:", n_b, "->", n_a)
if npass2 != npass or n_b != n_a:
    sys.exit(1)

open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ NOTICE.md 已更新（%d 字节）" % len(NOTICE.encode("utf-8")))
