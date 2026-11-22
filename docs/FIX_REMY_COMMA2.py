# -*- coding: utf-8 -*-
"""修复 <<print either(...)>>：字符串内部结尾的中文逗号删除，并保证参数间有英文逗号。"""
import re

p = r"E:\TAML\_dol\work\_remy_actions_text_zh.twee"
txt = open(p, encoding="utf-8").read()

def fix_block(m):
    inner = m.group(1)
    # 1) 字符串内部结尾的中文逗号/句号 -> 去掉（DoL 的 either 参数不需要句末标点）
    inner = re.sub(r'，(?=")', '', inner)
    inner = re.sub(r'。(?=")', '', inner)
    # 2) 引号之间缺逗号的补上
    inner = re.sub(r'(")\s*\n(\s*")', r'\1,\n\2', inner)
    inner = re.sub(r'(")\s+(")', r'\1, \2', inner)
    return "<<print either(" + inner + ")>>"

new, n = re.subn(r"<<print either\((.*?)\)>>", fix_block, txt, flags=re.S)
print("处理块:", n)
open(p, "w", encoding="utf-8").write(new)

# 复查
bad = 0
for m in re.finditer(r'，(?=")', new):
    bad += 1
print("字符串内结尾中文逗号残留:", bad)
