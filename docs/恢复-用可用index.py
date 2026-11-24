# -*- coding: utf-8 -*-
"""用可用版本的 index 替换当前，恢复可用状态。"""
import hashlib
import shutil

GOOD = r"E:\TAML\_dol\work\index_from_good.apk.html"
CUR = r"E:\TAML\_dol\work\index_modded6.html"

# 备份当前（可能已损坏的）
shutil.copy2(CUR, r"E:\TAML\_dol\work\index_modded6.html.bak_broken_maplebirch")
print("已备份损坏版本")

# 替换
shutil.copy2(GOOD, CUR)
print("已用可用版本替换")

# 校验
h = hashlib.md5(open(CUR, "rb").read()).hexdigest()
print("当前 index MD5:", h)
print("大小:", len(open(CUR, "rb").read()))
