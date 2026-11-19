"""构建后自动归档：每次签名完就复制一份到 archive/，永不覆盖。

用法（在签名之后调用）：
    python RC01_auto_archive.py <signed_apk_path> [说明]

会生成：
    archive/DoL-Lyra-0.5.12.13-CHS-modded_YYYYMMDD-HHMMSS_<说明>.apk
并追加到 archive/README.md
"""
import hashlib
import os
import re
import shutil
import sys
import zipfile
from datetime import datetime

ARCHIVE = r"E:\TAML\_dol\archive"


def apk_info(path):
    info = {"size": os.path.getsize(path)}
    try:
        z = zipfile.ZipFile(path)
        raw = z.read("assets/www/index.html")
        j = raw.find(b"[", raw.find(b"window.modDataValueZipList"))
        k = raw.find(b"]", j)
        if j > 0 and k > j:
            info["mods"] = len(re.findall(r'"[A-Za-z0-9+/=\s]{40,}"',
                                          raw[j + 1:k].decode("utf-8", "replace")))
        info["index"] = z.getinfo("assets/www/index.html").file_size
    except Exception:
        info["mods"] = 0
        info["index"] = 0
    return info


def main():
    if len(sys.argv) < 2:
        print("用法: python RC01_auto_archive.py <signed_apk> [说明]")
        return 1
    src = sys.argv[1]
    note = sys.argv[2] if len(sys.argv) > 2 else ""
    if not os.path.exists(src):
        print(f"❌ 文件不存在: {src}")
        return 1

    os.makedirs(ARCHIVE, exist_ok=True)
    mt = datetime.now()
    stem = mt.strftime("%Y%m%d-%H%M%S")
    safe_note = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", note)[:40] if note else ""
    tail = f"_{safe_note}" if safe_note else ""
    dst_name = f"DoL-Lyra-0.5.12.13-CHS-modded_{stem}{tail}.apk"
    dst = os.path.join(ARCHIVE, dst_name)

    shutil.copy2(src, dst)
    info = apk_info(dst)
    print(f"✅ 已归档: {dst_name}")
    print(f"   {info['size']/1048576:.2f} MB, mods={info['mods']}, index={info['index']/1048576:.2f} MB")

    # 追加到 README
    readme = os.path.join(ARCHIVE, "README.md")
    if os.path.exists(readme):
        s = open(readme, encoding="utf-8").read()
    else:
        s = "# DoL 整合包归档\n\n## 版本列表\n\n| 时间 | 大小 | 模组数 | index | 文件 |\n|---|---|---|---|---|\n"

    if dst_name not in s:
        row = (f"| {mt:%Y-%m-%d %H:%M} | {info['size']/1048576:.2f} MB | "
               f"{info['mods']} | {info['index']/1048576:.2f} MB | `{dst_name}` |\n")
        # 插到表格末尾
        m = re.search(r"(\| 时间 \| 大小 \| 模组数 \| index \| 文件 \|\n\|---\|---\|---\|---\|---\|\n)((?:\|.*\n)*)", s)
        if m:
            s = s[:m.end(2)] + row + s[m.end(2):]
        else:
            s = s.rstrip() + "\n" + row
        open(readme, "w", encoding="utf-8").write(s)
        print(f"   已记入 {readme}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
