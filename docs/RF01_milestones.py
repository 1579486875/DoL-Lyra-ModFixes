"""给归档 README 补充里程碑说明。"""
import os
import re
from datetime import datetime

ARCHIVE = r"E:\TAML\_dol\archive"
readme = os.path.join(ARCHIVE, "README.md")

MILESTONES = """
## 关键里程碑（按功能找版本）

| 特征 | 时间范围 | 怎么认 | 说明 |
|---|---|---|---|
| **最早的纯原版** | 11-18 12:41 | 159.24 MB / 33 模组 | Lyra 原包，无任何加成 |
| **翻译正常、未烤入 i18n** | **11-18 17:44 ~ 23:18** | **171.85~171.93 MB / 42~45 模组** | **index 97.4 MB**。靠运行时 `I18nTweeReplacer` 翻译，**你手机上那个 11.18 包就是这一批** |
| 开始烤入 i18n | 11-19 06:15 起 | 173.86 MB 起 | index 从 97.4 → 100+ MB |
| 加入大量补丁模组 | 11-19 06:32 起 | 模组数 50+ | 修复 widget / 补丁类模组陆续加入 |
| 当前最新 | 见表格最后一行 | 175.20 MB / 58 模组 | index 100.67 MB |

## 怎么区分「烤入前」和「烤入后」

看 `index` 列：

- **97 MB 左右** → 没烤入，**翻译由 ModI18N 运行时完成**
- **100 MB 左右** → 已烤入，**翻译写死在 index 里**

两者在游戏里的实际差别：

| | 运行时翻译 | 烤入 |
|---|---|---|
| 覆盖面 | ModI18N 原生逻辑 | 我自己的实现，需要额外过滤规则 |
| 单单词 UI（Beast / Orphanage） | 能翻 | **早期版本会漏，现已修复** |
| 补丁命中率 | DoLSims 有 72 条失配 | 全命中 |

## 出问题怎么回滚

1. 在表格里找到「翻译正常、未烤入 i18n」那批（11-18 17:44 ~ 23:18）
2. 随便挑一个装回去即可
3. 那批的补丁命中率不如现在，但**翻译是完整的**

## 每次新构建

```powershell
python E:\\TAML\\_dol\\work\\build.py "本次改了什么"
```

会自动：
- 重建 index
- 打包 + 签名
- **复制一份到本目录（永不覆盖）**
- 更新本 README 的表格
- 同时刷新 `out/` 的最新版
"""

if "## 关键里程碑（按功能找版本）" not in open(readme, encoding="utf-8").read():
    s = open(readme, encoding="utf-8").read()
    # 替换掉原来的空里程碑章节
    s = re.sub(r"## 关键里程碑\n\n.*?\n\n\n", "", s, flags=re.S)
    s = s.rstrip() + "\n" + MILESTONES
    open(readme, "w", encoding="utf-8").write(s)
    print("✅ 已补充里程碑说明")
else:
    print("（已存在）")

print(f"\n{readme}")
print(open(readme, encoding="utf-8").read()[-1500:])
