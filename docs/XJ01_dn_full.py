"""专门翻 displayName 里的英文（短标签被 UB01 的长度限制跳过）。"""
import html as H
import json
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
I18N = r"E:\TAML\_dol\work\i18n_dict.json"

FALLBACK = {
    "Anal:": "肛门：", "Analingus (Giving):": "舔肛（主动）：",
    "Analingus (Receiving):": "舔肛（被动）：", "Animated blinking:": "眨眼动画：",
    "Asphyxiation:": "窒息：", "Animal Transformations:": "动物转化：",
    "Average size of NPC penises:": "NPC 阴茎平均尺寸：",
    "Body writing:": "身体涂写：", "Breeding:": "繁殖：", "Chastity:": "贞操：",
    "Combat:": "战斗：", "Condoms:": "安全套：", "Corruption:": "堕落：",
    "Crossdressing:": "异装：", "Deviancy:": "异种癖：", "Exhibitionism:": "暴露癖：",
    "Feet:": "足部：", "Fertility:": "生育：", "Fetish:": "恋物：",
    "Footjob:": "足交：", "Gangbang:": "轮奸：", "Group sex:": "群交：",
    "Handjob:": "手交：", "Hypnosis:": "催眠：", "Incest:": "乱伦：",
    "Lactation:": "泌乳：", "Masochism:": "受虐癖：", "Masturbation:": "自慰：",
    "Menstruation:": "月经：", "Monsters:": "怪物：",
    "Nipple penetration:": "乳头插入：", "Nudity:": "裸体：", "Oral:": "口交：",
    "Orgasm:": "高潮：", "Oviposition:": "产卵：", "Parasites:": "寄生虫：",
    "Pregnancy:": "怀孕：", "Prostitution:": "卖淫：", "Rape:": "强奸：",
    "Sadism:": "施虐癖：", "Sex:": "性行为：", "Spanking:": "打屁股：",
    "Speech:": "言语：", "Squirting:": "潮吹：", "Strapon:": "穿戴式阳具：",
    "Tentacles:": "触手：", "Transformation:": "转化：", "Underwear:": "内衣：",
    "Vaginal:": "阴道：", "Virginity:": "童贞：", "Watersports:": "放尿：",
    "Zoom:": "缩放：", "Language:": "语言：", "Theme:": "主题：",
    "Font:": "字体：", "Sound:": "音效：", "Music:": "音乐：",
    "Volume:": "音量：", "Difficulty:": "难度：", "Save:": "存档：",
    "Load:": "读档：", "Export:": "导出：", "Import:": "导入：",
    "Cheat mode:": "作弊模式：", "Genitals:": "生殖器：", "Gender:": "性别：",
    "Penis size:": "阴茎大小：", "Breast size:": "胸部尺寸：",
    "Skin colour:": "肤色：", "Hair style:": "发型：", "Fringe style:": "刘海样式：",
    "Body shape:": "身形：", "Body type:": "体型：", "Awareness:": "意识：",
    "Background:": "角色背景：", "Body size:": "体型大小：", "Demeanour:": "举止：",
    "Breast sensitivity:": "胸部敏感度：", "Genital sensitivity:": "生殖器敏感度：",
    "Mouth sensitivity:": "口腔敏感度：", "Bottom sensitivity:": "后穴敏感度：",
    "Alcohol tolerance:": "酒精耐受度：", "Eye colour:": "瞳色：",
    "Hair colour:": "发色：", "Hair length:": "发长：",
}


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")

    print("加载 i18n...")
    d = json.load(open(I18N, "r", encoding="utf-8"))
    trans = {}
    for it in d["typeB"]["TypeBInputStoryScript"]:
        f, t = it.get("f"), it.get("t")
        if f and t and f != t and len(f) <= 60:
            trans[f.strip()] = t
    print(f"  短条目 {len(trans)} 条")

    total = 0

    def repl(m):
        nonlocal total
        pre, en, post = m.group(1), m.group(2), m.group(3)
        if not re.match(r"^[A-Za-z]", en):
            return m.group(0)
        cn = trans.get(en.strip()) or FALLBACK.get(en)
        if not cn:
            return m.group(0)
        total += 1
        return pre + cn + post

    data = re.sub(r'(displayName:\s*")([^"]{1,60})(")', repl, data)
    print(f"  displayName 翻译 {total} 处")

    if total:
        open(HTML, "wb").write(data.encode("utf-8"))
        print(f"\n合计 {total} 处")

    g = H.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))
    remain = sorted(set(re.findall(r'displayName:\s*"([A-Za-z][^"]{1,60})"', g)))
    print(f"\n剩余纯英文 displayName: {len(remain)}")
    for r in remain[:25]:
        print(f"  {r!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
