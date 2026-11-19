"""U01：安装失败深度诊断 —— 查 META-INF 未保护文件 / ZIP 异常 / 压缩方法。"""
import os
import struct
import zipfile
from collections import Counter

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"


def diag(path, label):
    print("=" * 100)
    print(f"{label}  {os.path.basename(path)}  ({os.path.getsize(path)/1048576:.2f} MB)")
    print("=" * 100)
    z = zipfile.ZipFile(path)

    # 1) META-INF 内容分类
    meta = [n for n in z.namelist() if n.startswith("META-INF/")]
    ver_files = [n for n in meta if n.endswith(".version")]
    props = [n for n in meta if n.endswith(".properties")]
    sig_files = [n for n in meta if n.endswith((".SF", ".RSA", ".DSA", ".EC")) or n == "META-INF/MANIFEST.MF"]
    other = [n for n in meta if n not in ver_files + props + sig_files]

    print(f"  META-INF 共 {len(meta)} 个")
    print(f"    .version     : {len(ver_files)}  ← 未受签名保护")
    print(f"    .properties  : {len(props)}  ← 未受签名保护")
    print(f"    签名文件      : {len(sig_files)}")
    print(f"    其他          : {len(other)} {other[:5]}")

    # 2) MANIFEST.MF 覆盖范围
    mf = z.read("META-INF/MANIFEST.MF").decode("utf-8", "replace")
    mf_names = set()
    for line in mf.split("\n"):
        if line.startswith("Name: "):
            mf_names.add(line[6:].strip())
    print(f"  MANIFEST.MF 保护 {len(mf_names):,} 个条目")
    print(f"  ZIP 总条目 {len(z.namelist()):,}")

    # 哪些在 META-INF 但不在 MANIFEST
    unprotected = [n for n in meta if n not in mf_names and not n.endswith((".SF", ".RSA", ".DSA", ".EC")) and n != "META-INF/MANIFEST.MF"]
    print(f"  META-INF 里未保护: {len(unprotected)}")
    for n in unprotected[:5]:
        print(f"    {n}")

    # 3) 压缩方法分布
    methods = Counter()
    zip64 = 0
    for info in z.infolist():
        methods[info.compress_type] += 1
        if info.file_size > 0xFFFFFFFF or info.compress_size > 0xFFFFFFFF:
            zip64 += 1
    print(f"  压缩方法: {dict(methods)}  （0=store, 8=deflate）")
    print(f"  ZIP64 条目: {zip64}")

    # 4) 是否有异常的 external_attr / 文件名
    weird = [i.filename for i in z.infolist()
             if any(c in i.filename for c in ("\\", ":", "?", "*", "\"", "<", ">", "|"))
             and not i.filename.startswith("assets/www/img/")]
    print(f"  文件名含异常字符: {len(weird)} {weird[:3]}")

    # 5) 首条目是否 AndroidManifest（zipalign 要求）
    first = z.namelist()[0] if z.namelist() else ""
    print(f"  首条目: {first}")

    # 6) 是否有重复条目
    names = z.namelist()
    print(f"  重复条目: {len(names) - len(set(names))}")

    print()


diag(APK, "modded")
diag(VAN, "vanilla")
