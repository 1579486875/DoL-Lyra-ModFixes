"""修 cheatsBody：显示中文但 $player.gender_body 必须存 m/f/a。

vanilla: _bodyTypes = ["masculine","feminine","androgynous"]
         <<set $player.gender_body to _bodyTypes[_i].charAt(0)>>   -> m/f/a
modded : _bodyTypes = ["男性化","女性化","中性化"]
         charAt(0) -> 男/女/中   ← 破坏 JS 里所有 === "m"/"f"/"a" 判断
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

data = open(HTML, "rb").read().decode("utf-8", "replace")
g = H.unescape(data)

print("=" * 80)
print("当前 cheatsBody")
print("=" * 80)
m = re.search(r'<<widget "cheatsBody">>(.*?)<</widget>>', g, re.S)
if not m:
    print("❌ 未找到")
    sys.exit(1)
old_body = m.group(1)
print(old_body[:900])

# 构造新 body
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

# 先恢复被我上一轮改坏的 {m:'m',f:'f',a:'a'}
fixed = g.replace("{m:'m',f:'f',a:'a'}", "_bodyKeys[_i]")
n_restore = g.count("{m:'m',f:'f',a:'a'}")

if fixed == g and "cheatsBody" in g:
    print("\n（无上一轮残留，直接替换 widget 主体）")

# 替换整个 widget 主体
new_block = '<<widget "cheatsBody">>' + NEW_BODY + '<</widget>>'
old_block = m.group(0)
if old_block in fixed:
    fixed = fixed.replace(old_block, new_block, 1)
    print("\n✅ 已替换 cheatsBody 主体")
else:
    print("\n❌ 替换失败")
    sys.exit(1)

data = H.escape(fixed, quote=False)
open(HTML, "wb").write(data.encode("utf-8"))
print(f"写出: {HTML}")

# 校验
g2 = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
print("\n=== 校验 ===")
print(f"  _bodyKeys 出现: {len(re.findall('_bodyKeys', g2))}")
print(f"  中文键对象残留: {len(re.findall(chr(123) + chr(39) + '男', g2))}")
print(f"  charAt(0) 存值残留: {len(re.findall('gender_body to _bodyTypes.blogspot', g2))}")
m2 = re.search(r'<<widget "cheatsBody">>(.*?)<</widget>>', g2, re.S)
if m2:
    print("\n[新 body]")
    print(m2.group(1)[:800])
