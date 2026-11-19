"""提取 vanilla 的 index 到 work 目录，供 HTTP 测试。"""
import os
import zipfile

VAN = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-vanilla.apk"
OUT = r"E:\TAML\_dol\work\index_vanilla.html"

z = zipfile.ZipFile(VAN)
data = z.read("assets/www/index.html")
open(OUT, "wb").write(data)
print(f"已提取: {OUT}  ({len(data):,} 字节)")
