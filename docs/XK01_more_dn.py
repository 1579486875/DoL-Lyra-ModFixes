"""补第二批 displayName（设置界面常见项）+ 修 regress.py 的 either 检测。"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
REGRESS = r"E:\TAML\_dol\work\regress.py"

MORE = {
    "Balls:": "睾丸：",
    "Bees:": "蜜蜂：",
    "Black Wolf beast type:": "黑狼兽型：",
    "Blind stats mode:": "盲测属性模式：",
    "Body type displayed:": "显示的体型：",
    "Bodywriting images:": "身体涂写图像：",
    "Bottom size:": "后穴尺寸：",
    "Breastfeeding:": "哺乳：",
    "Character lighting:": "角色光照：",
    "Closed sidebar stats:": "收起侧栏属性：",
    "Closed sidebar time:": "收起侧栏时间：",
    "Combat animations:": "战斗动画：",
    "Combat controls:": "战斗操作：",
    "Combat images:": "战斗图像：",
    "Condom display:": "安全套显示：",
    "Cost of clothing:": "衣物价格：",
    "Cost of furniture:": "家具价格：",
    "Base NPC pregnancy chance:": "NPC 基础怀孕率：",
    "Base player pregnancy chance:": "玩家基础怀孕率：",
    "Beast attraction split by gender appearance:": "野兽吸引力按性别外观分配：",
    "Beasts who are attracted to men:": "被男性吸引的野兽比例：",
    "Beasts who are attracted to women:": "被女性吸引的野兽比例：",
    "Average size of women's breasts:": "女性胸部平均尺寸：",
    "Bailey's rent:": "贝利的租金：",
    "Angel/Devil TF colour components:": "天使/恶魔转化配色分量：",
    "Cheat mode:": "作弊模式：",
    "Difficulty:": "难度：",
    "Font size:": "字体大小：",
    "Line height:": "行高：",
    "Paragraph:": "段落：",
    "Overlay:": "遮罩层：",
    "Sidebar:": "边栏：",
    "Popup:": "弹窗：",
    "Text animation effects:": "文本动画效果：",
    "Image loading:": "图像加载：",
    "Rendering:": "渲染：",
    "Game zoom:": "游戏缩放：",
    "Advanced settings:": "高级设置：",
    "More info:": "更多信息：",
    "Displayed frame rate:": "显示帧率：",
    "Map:": "地图：",
    "Popups:": "弹窗：",
    "Sidebar stats:": "侧栏属性：",
    "Crop yield:": "作物产量：",
    "Dildos:": "假阳具：",
    "Divine Transformations:": "神圣转化：",
    "Freckles:": "雀斑：",
    "Natural Skintone:": "自然肤色：",
    "Cost of lewd clothes:": "淫秽衣物价格：",
    "Cost of school clothes:": "校服价格：",
    "Cost of underwear:": "内衣价格：",
    "Starting season:": "起始季节：",
    "Game difficulty:": "游戏难度：",
    "Ironman mode:": "铁人模式：",
    "Combat:": "战斗：",
    "Starting season:": "起始季节：",
    "Game difficulty:": "游戏难度：",
    "Ironman mode:": "铁人模式：",
    "Natural Skintone:": "自然肤色：",
    "Freckles:": "雀斑：",
    "Cost of lewd clothes:": "淫秽衣物价格：",
    "Cost of school clothes:": "校服价格：",
    "Cost of underwear:": "内衣价格：",
    "Mouth:": "口腔：",
    "Hands:": "手部：",
    "Nipples:": "乳头：",
    "Penis:": "阴茎：",
    "Vagina:": "阴道：",
    "Anus:": "肛门：",
    "Thighs:": "大腿：",
}


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    total = 0
    for en, cn in MORE.items():
        pat = f'displayName: "{en}"'
        pat_cn = f'displayName: "{cn}"'
        if pat in data:
            n = data.count(pat)
            data = data.replace(pat, pat_cn)
            total += n
            print(f"  ✅ {en!r} -> {cn!r} ({n})")
    if total:
        open(HTML, "wb").write(data.encode("utf-8"))
        print(f"\n合计 {total} 处")

    g = H.unescape(data)
    remain = sorted(set(re.findall(r'displayName:\s*"([A-Za-z][^"]{1,60})"', g)))
    print(f"\n剩余英文 displayName: {len(remain)}")

    # ---- 修 regress.py 的 either 检测（排除字符串内）----
    rs = open(REGRESS, encoding="utf-8").read()
    OLD = '''        inner = g[m.end():i - 1]
        base = re.sub(r'"[^"]*"', "", inner)
        if "，" in base:
            n += 1'''
    NEW = '''        inner = g[m.end():i - 1]
        # 先去掉所有字符串字面量（含单双引号），再看剩下的代码里有没有全角逗号
        base = re.sub(r'"(?:[^"\\\\]|\\\\.)*"', '""', inner)
        base = re.sub(r"'(?:[^'\\\\]|\\\\.)*'", "''", base)
        if "，" in base:
            n += 1'''
    if OLD in rs:
        rs = rs.replace(OLD, NEW, 1)
        open(REGRESS, "w", encoding="utf-8").write(rs)
        print("✅ regress.py 的 either 检测已排除字符串内容")
    else:
        print("⚠️ regress.py 未找到 either 检测块")
    return 0


if __name__ == "__main__":
    sys.exit(main())
