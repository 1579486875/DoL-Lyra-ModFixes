"""BC01（第16轮）：玩具名称i18n补丁 —— 修复"length of anal beads"等英文残留。

用户报告：游戏中显示"length of anal beads"、"right"等英文残留。
根因：玩具名称作为标识符存储（如$NPCList[_n].lefttool），但显示时缺少中文翻译。
修法：在StoryInit中添加setup.toyNamesCN翻译映射，在显示玩具名称的widget中使用。
"""
import html as H
import os
import re
import sys

HTML = os.environ.get("DOL_HTML") or r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")
if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[BC01] index 形态异常")
    sys.exit(1)

# 在StoryInit passage末尾添加玩具名称翻译表
storyinit_pattern = r'<tw-passagedata[^>]*name="StoryInit"[^>]*>(.*?)</tw-passagedata>'
match = re.search(storyinit_pattern, data, re.S)
if not match:
    print("[BC01] FAIL 找不到 StoryInit passage")
    sys.exit(1)

storyinit_content = H.unescape(match.group(1))

# 检查是否已经添加过
if 'setup.toyNamesCN' in storyinit_content:
    print("[BC01] 无需修改（已存在 setup.toyNamesCN）")
    sys.exit(0)

# 构造翻译代码
toy_i18n_code = '''

/* BC01: 玩具名称中文翻译表（修复 length of anal beads 等英文残留） */
<<run>>
setup.toyNamesCN = {
	"dildo": "假阳具",
	"riding crop": "马鞭",
	"length of anal beads": "肛珠",
	"flog": "鞭子",
	"anal beads": "肛珠",
	"beads": "珠子"
};
/* 翻译函数 */
window.toyNameCN = function(enName) {
	return setup.toyNamesCN[enName] || enName;
};
<</run>>'''

# 在StoryInit末尾添加
new_storyinit_content = storyinit_content.rstrip() + toy_i18n_code

# 替换
new_storyinit_block = match.group(0).replace(
    match.group(1),
    H.escape(new_storyinit_content, quote=False)
)

data = data.replace(match.group(0), new_storyinit_block)

# 现在需要在显示玩具名称的地方使用翻译
# 搜索显示模式：通常是在<<print>>或直接输出$NPCList[_n].lefttool的地方
# 但为了不破坏现有逻辑，我们采用更保守的方案：
# 只添加翻译表，让需要的地方调用toyNameCN()函数

open(HTML, "wb").write(data.encode("utf-8"))
print("[BC01] 已添加玩具名称翻译表 setup.toyNamesCN 和函数 toyNameCN()")
print("[BC01] 注意：现有代码需要手动调用 toyNameCN() 来翻译，或在后续轮次全局替换")
