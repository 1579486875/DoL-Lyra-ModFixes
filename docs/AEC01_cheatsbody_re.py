"""修 cheatsBody（正则版）。"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

NEW_BODY = '''
\t<<set _bodyTypes to ["男性化", "女性化", "中性化"]>>
\t<<set _bodyKeys to ["m", "f", "a"]>>

\t<<capture _i>>
\t\t<<for _i = 0; _i < _bodyTypes.length; _i++>>
\t\t\t<span @class="$player.gender_body is _bodyKeys[_i] ? 'goldLink' : 'unselected'">
\t\t\t\t<<link _bodyTypes[_i]>>
\t\t\t\t\t<<set $player.gender_body to _bodyKeys[_i]>>
\t\t\t\t\t<<replace "#statsBodyType">><<cheatsBody>><</replace>><<updatesidebarimg>>
\t\t\t\t<</link>>
\t\t\t</span>\t<<= _i lt _bodyTypes.length - 1 ? "|" : "">>
\t\t<</for>>
\t<</capture>>
'''

data = open(HTML, "rb").read().decode("utf-8", "replace")

# 用正则匹配整个 widget（非贪婪）
pat_esc = re.compile(
    r'&lt;&lt;widget "cheatsBody"&gt;&gt;.*?&lt;&lt;/widget&gt;&gt;', re.S)
pat_raw = re.compile(r'<<widget "cheatsBody">>.*?<</widget>>', re.S)

new_esc = '&lt;&lt;widget "cheatsBody"&gt;&gt;' + H.escape(NEW_BODY, quote=False) + '&lt;&lt;/widget&gt;&gt;'
new_raw = '<<widget "cheatsBody">>' + NEW_BODY + '<</widget>>'

done = 0
if pat_esc.search(data):
    n = len(pat_esc.findall(data))
    data = pat_esc.sub(new_esc, data)
    done = n
    print(f"✅ 转义形态替换 {n} 处")
elif pat_raw.search(data):
    n = len(pat_raw.findall(data))
    data = pat_raw.sub(new_raw, data)
    done = n
    print(f"✅ 原始形态替换 {n} 处")

if not done:
    print("❌ 未找到 cheatsBody widget")
    sys.exit(1)

open(HTML, "wb").write(data.encode("utf-8"))
print(f"写出: {HTML}")

g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n=== 校验 ===")
print(f"  _bodyKeys 出现: {len(re.findall('_bodyKeys', g2))}")
print(f"  中文键对象残留: {len(re.findall(chr(123) + chr(39) + '男', g2))}")
m2 = re.search(r'<<widget "cheatsBody">>(.*?)<</widget>>', g2, re.S)
if m2:
    print("\n[新 body]")
    print(m2.group(1)[:700])
