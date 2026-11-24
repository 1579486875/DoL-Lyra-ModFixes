# -*- coding: utf-8 -*-
"""把 cdp_flow.js 的 passage 取值改为内联自包含表达式。"""
import re

p = r"E:\TAML\_dol\work\cdp_flow.js"
s = open(p, encoding="utf-8").read()

# 内联表达式：不依赖外部辅助函数
INLINE = (
    '(function(){'
    'try{'
    'var S=window.SugarCube||{};'
    'var st=S.State;'
    'if(st){'
    'if(typeof st.passage==="string"&&st.passage)return st.passage;'
    'if(st.current&&typeof st.current.title==="string")return st.current.title;'
    '}'
    'var el=document.querySelector("#passages .passage:last-child");'
    'if(el)return el.getAttribute("data-passage")||el.id||null;'
    'return null;'
    '}catch(e){return null;}'
    '})()'
)

# 替换所有引用 __navPassage 的地方
cnt = s.count("window.__navPassage()")
if cnt:
    s = s.replace('"window.__navPassage()"', '"%s"' % INLINE.replace('"', '\\"'))
    print("替换 __navPassage 调用:", cnt)

# 如果还有旧的裸 State 表达式
OLD = 'const actual = await evalJs("typeof State!==\'undefined\' ? State.passage : null");'
if OLD in s:
    s = s.replace(OLD, 'const actual = await evalJs("%s");' % INLINE.replace('"', '\\"'))
    print("替换裸 State 表达式")

open(p, "w", encoding="utf-8").write(s)
print("✅ 写入")

# 校验
import subprocess
r = subprocess.run(["node", "--check", p], capture_output=True, text=True, encoding="utf-8")
print("语法检查:", "OK" if r.returncode == 0 else r.stderr[:200])

# 展示改后的行
for m in re.finditer(r"const actual = await evalJs\(.{0,120}", s):
    print("改后:", m.group(0)[:160])
