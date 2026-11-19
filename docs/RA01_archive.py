"""建立归档：把所有历史签名包按时间线整理到 archive/，并生成索引 README。

策略：
  - signed*/ 里的 APK = 可安装的最终产物 -> 全部归档
  - build*_unsigned.apk = 中间产物 -> 只在 archive/_unsigned/ 留最近 3 个
  - 按「日期-时间」重命名，一眼能看出先后
"""
import hashlib
import os
import re
import shutil
import zipfile
from datetime import datetime

WORK = r"E:\TAML\_dol\work"
OUT = r"E:\TAML\_dol\out"
ARCHIVE = r"E:\TAML\_dol\archive"

os.makedirs(ARCHIVE, exist_ok=True)
UNSIGNED_DIR = os.path.join(ARCHIVE, "_unsigned")
os.makedirs(UNSIGNED_DIR, exist_ok=True)


def apk_info(path):
    """读 APK 的版本信息。"""
    info = {"size": os.path.getsize(path)}
    try:
        z = zipfile.ZipFile(path)
        names = z.namelist()
        info["entries"] = len(names)
        # 模组数
        raw = z.read("assets/www/index.html")
        j = raw.find(b"[", raw.find(b"window.modDataValueZipList"))
        k = raw.find(b"]", j)
        if j > 0 and k > j:
            seg = raw[j + 1:k].decode("utf-8", "replace")
            info["mods"] = len(re.findall(r'"[A-Za-z0-9+/=\s]{40,}"', seg))
        # index 大小
        try:
            info["index"] = z.getinfo("assets/www/index.html").file_size
        except Exception:
            info["index"] = 0
    except Exception as e:
        info["error"] = str(e)
    return info


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


rows = []

# ---- 1) signed* 目录里的 APK ----
print("扫描 signed* ...")
dirs = sorted(
    [d for d in os.listdir(WORK) if d.startswith("signed") and os.path.isdir(os.path.join(WORK, d))],
    key=lambda x: (len(x), x),
)
for d in dirs:
    dp = os.path.join(WORK, d)
    apks = [f for f in os.listdir(dp) if f.lower().endswith(".apk")]
    if not apks:
        continue
    src = os.path.join(dp, apks[0])
    mt = datetime.fromtimestamp(os.path.getmtime(src))
    stem = mt.strftime("%Y%m%d-%H%M%S")
    dst_name = f"DoL-Lyra-0.5.12.13-CHS-modded_{stem}_{d}.apk"
    dst = os.path.join(ARCHIVE, dst_name)
    if not os.path.exists(dst):
        shutil.move(src, dst)
    info = apk_info(dst)
    rows.append({
        "name": dst_name,
        "time": mt.strftime("%Y-%m-%d %H:%M"),
        "size_mb": round(info["size"] / 1048576, 2),
        "mods": info.get("mods", 0),
        "index_mb": round(info.get("index", 0) / 1048576, 2),
        "src": d,
    })
    print(f"  {mt:%m-%d %H:%M}  {info['size']/1048576:6.2f} MB  mods={info.get('mods',0):>3}  {d}")

# ---- 2) build*_unsigned 只留最近 3 个 ----
print("\n处理 build*_unsigned ...")
builds = []
for f in os.listdir(WORK):
    if re.match(r"build\d*_unsigned\.apk$", f):
        p = os.path.join(WORK, f)
        builds.append((os.path.getmtime(p), f, p))
builds.sort(reverse=True)
for i, (mt, f, p) in enumerate(builds):
    if i < 3:
        dst = os.path.join(UNSIGNED_DIR, f)
        if not os.path.exists(dst):
            shutil.move(p, dst)
        print(f"  保留 {f}")
    else:
        os.remove(p)
print(f"  保留最近 3 个，删除其余 {max(0, len(builds)-3)} 个")

# ---- 3) 生成 README ----
rows.sort(key=lambda r: r["time"])
lines = [
    "# DoL 整合包归档",
    "",
    f"生成时间：{datetime.now():%Y-%m-%d %H:%M}",
    "",
    "## 说明",
    "",
    "- 每个文件都是**已签名、可直接安装**的 APK",
    "- 文件名格式：`DoL-Lyra-0.5.12.13-CHS-modded_日期-时间_序号.apk`",
    "- `_unsigned/` 目录是最新 3 次构建的未签名中间产物（仅供回滚，不能直接安装）",
    "- `out/` 目录下的 `DoL-Lyra-0.5.12.13-CHS-modded.apk` 永远是最新版本",
    "",
    "## 版本列表（按时间正序）",
    "",
    "| 时间 | 大小 | 模组数 | index | 文件 |",
    "|---|---|---|---|---|",
]
for r in rows:
    lines.append(f"| {r['time']} | {r['size_mb']} MB | {r['mods']} | {r['index_mb']} MB | `{r['name']}` |")

lines += [
    "",
    "## 怎么找回某个版本",
    "",
    "1. **按时间找**：文件名里的 `YYYYMMDD-HHMMSS` 就是构建时刻",
    "2. **按功能找**：看下面「关键里程碑」表",
    "3. **校验完整性**：`Get-FileHash <文件> -Algorithm SHA256`",
    "",
    "## 关键里程碑",
    "",
    "（构建完成后手工补充说明）",
    "",
]

readme = os.path.join(ARCHIVE, "README.md")
open(readme, "w", encoding="utf-8").write("\n".join(lines))
print(f"\n索引已写入: {readme}")
print(f"归档目录共 {len(rows)} 个可安装包")
