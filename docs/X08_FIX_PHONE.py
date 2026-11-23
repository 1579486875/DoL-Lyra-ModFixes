# -*- coding: utf-8 -*-
"""在 variablesStatic 里初始化 $Phone（SugarCube 变量，补丁读取前必须先存在）。"""
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))

# 锚点：variablesStatic 里 <<set setup.test to "testing">> 之后
OLD = '&lt;&lt;set setup.test to "testing"&gt;&gt;'
NEW = ('&lt;&lt;set setup.test to "testing"&gt;&gt;\n'
       '&lt;&lt;if $Phone is undefined&gt;&gt;&lt;&lt;set $Phone to {}&gt;&gt;&lt;&lt;/if&gt;&gt;\n'
       '&lt;&lt;if $Phone.TaskDanger is undefined&gt;&gt;&lt;&lt;set $Phone.TaskDanger to 0&gt;&gt;&lt;&lt;/if&gt;&gt;\n'
       '&lt;&lt;if $Phone.Task is undefined&gt;&gt;&lt;&lt;set $Phone.Task to 0&gt;&gt;&lt;&lt;/if&gt;&gt;\n'
       '&lt;&lt;if $Phone.TaskRun is undefined&gt;&gt;&lt;&lt;set $Phone.TaskRun to 0&gt;&gt;&lt;&lt;/if&gt;&gt;')

if OLD not in raw:
    print("❌ 锚点未找到")
    sys.exit(1)

cnt = raw.count(OLD)
raw2 = raw.replace(OLD, NEW, 1)
print("注入 $Phone 初始化（%d 处锚点，替换第 1 处）" % cnt)

npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
print("passage:", npass, "->", npass2)
if npass2 != npass:
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("✅ 写入")
