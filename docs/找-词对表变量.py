# -*- coding: utf-8 -*-
"""定位这个词对表的变量名与替换函数。"""
import re
import zipfile

z = zipfile.ZipFile(r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
h = z.read("assets/www/index.html").decode("utf-8", "replace")

KEY = "dogboys,狗男"
i = h.find(KEY)
print("表位置:", i)

# 往前找这个字符串的起始引号与前面的变量名
j = i
while j > 0 and h[j] != '"':
    j -= 1
print("字符串起始:", j)
print("前 200 字符:", h[max(0, j - 200):j + 50].replace("\n", " "))

# 找赋值形式 xxx = " ... "
m = re.search(r"([A-Za-z_$][\w$\.]{1,60})\s*=\s*\"[^\"]*$", h[max(0, j - 3000):j + 1], re.S)
if m:
    print("\n变量名:", m.group(1))
else:
    # 可能是函数参数或数组元素
    print("\n前 600 字符:", h[max(0, j - 600):j + 60].replace("\n", " "))

# 找这个表怎么被使用（split('|') -> split(',')）
print("\n=== 搜 split(',') / split('|') 的用法 ===")
for mm in list(re.finditer(r"split\(['\"]\|\s*,\s*['\"]\)|split\(['\"]\|\s*['\"]\)", h))[:10]:
    seg = h[max(0, mm.start() - 400):mm.start() + 400]
    print("\n@%d: %s" % (mm.start(), seg.replace("\n", " ")[:700]))
