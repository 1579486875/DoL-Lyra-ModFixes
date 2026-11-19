"""一次性翻译所有剩余 103 个英文 displayName。"""
import html as H
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

ALL = {
    "Date format:": "日期格式：",
    "Display passage count:": "显示段落计数：",
    "Display play time:": "显示游玩时间：",
    "Display traits:": "显示特质：",
    "Double Anal:": "双重肛交：",
    "Double Vaginal:": "双重阴道：",
    "Enable clothing replacement warning:": "启用换装提醒：",
    "Enable combat tools:": "启用战斗工具：",
    "Enable movement by clicking on map:": "启用点击地图移动：",
    "Enable numbered link navigation:": "启用编号链接导航：",
    "Enable numpad:": "启用数字键盘：",
    "Enable renderer debugger:": "启用渲染调试器：",
    "Encounter rate:": "遭遇频率：",
    "Facesitting:": "坐脸：",
    "Fertility references:": "生育相关提示：",
    "Flat light:": "平光：",
    "Foot fetish:": "恋足：",
    "Forced crossdressing:": "强制异装：",
    "Generic NPC pregnancy:": "普通 NPC 怀孕：",
    "Genitalia: ": "生殖器官：",
    "Glow:": "辉光：",
    "Gradient:": "渐变：",
    "Great Hawk beast type:": "巨鹰兽型：",
    "Half-closed eyes:": "半睁眼：",
    "Hide player nudity in menus:": "菜单中隐藏玩家裸体：",
    "History depth:": "历史记录深度：",
    "Horses:": "马：",
    "Human pregnancy length:": "人类怀孕时长：",
    "Images:": "图像：",
    "Likelihood of adults being virgins:": "成年人为处子/处女的概率：",
    "Likelihood of young adults being virgins:": "年轻成年人为处子/处女的概率：",
    "Likelihood that NPCs have dark skin:": "NPC 深色皮肤的概率：",
    "Lurkers:": "潜伏者：",
    "Maximum bottom size:": "后穴最大尺寸：",
    "Maximum breast size:": "胸部最大尺寸：",
    "Maximum penis size:": "阴茎最大尺寸：",
    "Menstrual cycle:": "月经周期：",
    "Minimum bottom size:": "后穴最小尺寸：",
    "Minimum breast size:": "胸部最小尺寸：",
    "Minimum penis size:": "阴茎最小尺寸：",
    "Move the map above the map links:": "把地图移到地图链接上方：",
    "Multiple penetration with sex toys:": "性玩具多重插入：",
    "Multiple wardrobes:": "多套衣柜：",
    "NNPC/LI pregnancy:": "具名 NPC / 恋人怀孕：",
    "NPC anal pregnancy:": "NPC 肛门怀孕：",
    "NPC attraction split by gender appearance:": "NPC 吸引力按性别外观分配：",
    "NPC silhouettes:": "NPC 剪影：",
    "NPCs who are attracted to men:": "被男性吸引的 NPC 比例：",
    "NPCs who are attracted to women:": "被女性吸引的 NPC 比例：",
    "Night Monster beast type:": "夜魔兽型：",
    "Notes auto saving:": "笔记自动保存：",
    "Nude gender appearance:": "裸体性别外观：",
    "Only replace beasts with monsters while hallucinating:": "仅在幻觉时把野兽替换为怪物：",
    "Overlay font size:": "遮罩层字体大小：",
    "Overlay line height:": "遮罩层行高：",
    "PC anal pregnancy:": "玩家肛门怀孕：",
    "Parasite pregnancy:": "寄生虫怀孕：",
    "Passage font size:": "正文段落字体大小：",
    "Passage line height:": "正文段落行高：",
    "Pepper spray display:": "防狼喷雾显示：",
    "Percentage of beasts attracted to you that are male:": "被吸引的野兽中雄性占比：",
    "Percentage of beasts that are replaced with monster girls or boys:": "野兽被替换为怪物女孩/男孩的百分比：",
    "Percentage of men that have vaginas:": "有阴道的男性比例：",
    "Percentage of other victims that are male:": "其他受害者中男性占比：",
    "Percentage of people attracted to you that are male:": "被吸引的人中男性占比：",
    "Percentage of women that have penises:": "有阴茎的女性比例：",
    "Percentage of women that have strap-on penises:": "有穿戴式阳具的女性比例：",
    "Plantpeople:": "植物人：",
    "Player egg laying:": "玩家产卵：",
    "Player pregnancy with beasts:": "玩家与野兽怀孕：",
    "Player pregnancy with humans:": "玩家与人类怀孕：",
    "Pregnancy mode:": "怀孕模式：",
    "Pronoun: ": "人称代词：",
    "Pubic hair:": "阴毛：",
    "Reduced line height:": "紧凑行高：",
    "Require confirmation on delete:": "删除时需确认：",
    "Require confirmation on load:": "读取时需确认：",
    "Require confirmation on save:": "保存时需确认：",
    "Ruined orgasms:": "高潮中断：",
    "Show caption text in sidebar:": "侧栏显示状态文字：",
    "Show clickable areas on maps:": "地图上显示可点区域：",
    "Show clothing description in sidebar:": "侧栏显示衣物描述：",
    "Show history controls:": "显示历史操作按钮：",
    "Sidebar Tips:": "侧栏提示：",
    "Sidebar font size:": "侧栏字体大小：",
    "Sidebar images:": "侧栏图像：",
    "Sidebar line height:": "侧栏行高：",
    "Skill check display:": "技能检定显示：",
    "Skip confirmation when viewing extra stats:": "查看额外属性时跳过确认：",
    "Slimes:": "史莱姆：",
    "Slugs:": "蛞蝓：",
    "Spiders:": "蜘蛛：",
    "Spotlight height:": "聚光高度：",
    "Spotlight width:": "聚光宽度：",
    "Spotlight:": "聚光灯：",
    "Swarms:": "虫群：",
    "Time style:": "时间样式：",
    "Use 'narrow screen' version of market inventory:": "使用「窄屏版」市集清单：",
    "Vore:": "吞食：",
    "Wasps:": "黄蜂：",
    "Whips:": "鞭子：",
    "Wolf pregnancy length:": "狼怀孕时长：",
    "Y offset:": "Y 轴偏移：",
}


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")
    total = 0
    miss = []
    for en, cn in ALL.items():
        a = f'displayName: "{en}"'
        b = f'displayName: "{cn}"'
        if a in data:
            n = data.count(a)
            data = data.replace(a, b)
            total += n
        else:
            miss.append(en)

    print(f"翻译 {total} 处")
    if miss:
        print(f"未命中 {len(miss)} 个:")
        for m in miss[:10]:
            print(f"  {m!r}")

    if total:
        open(HTML, "wb").write(data.encode("utf-8"))
        print(f"写出 {HTML}")

    g = H.unescape(data)
    CJK = re.compile(r"[\u4e00-\u9fff]")
    remain = sorted(set(x for x in re.findall(r'displayName:\s*"([^"]{1,70})"', g)
                        if not CJK.search(x)))
    print(f"\n剩余纯英文 displayName: {len(remain)}")
    for r in remain[:10]:
        print(f"  {r!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
