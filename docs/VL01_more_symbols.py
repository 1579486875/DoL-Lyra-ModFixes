"""补 i18n 引用但未定义的 setup 函数。

缺失清单（经 vanilla 对照确认，都是 modded 独有）：
  setup.BODYPARTS_CN_NAME(x)     身体部位名
  setup.CAFE_FOOD_CN(x)          咖啡厅食物名
  setup.DirectionCN(x)           方向
  setup.NPC_CN_TOOLNAME(x)       性玩具名
  setup.brothelshowType_CN(x)    妓院演出类型
  setup.update_cloth_cn(x)       衣物名
  setup.T                        翻译表容器（setup.T.npcClothesItems）

全部实现为「查表，查不到返回原值」，绝不抛错。
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

BLOCK = '''<<script>>
(function () {
    if (!window.SugarCube || !SugarCube.setup) return;
    var st = SugarCube.setup;
    if (st.__i18nHelpersInstalled) return;
    st.__i18nHelpersInstalled = true;

    function safe(x) { return (x === null || x === undefined) ? "" : String(x); }

    function mk(table, extra) {
        return function (x) {
            var s = safe(x);
            var k = s.toLowerCase().trim();
            if (table && Object.prototype.hasOwnProperty.call(table, k)) return table[k];
            if (extra) {
                var r = extra(s);
                if (r !== null && r !== undefined) return r;
            }
            return s;
        };
    }

    /* 身体部位 */
    st.BODYPARTS_CN_NAME = mk({
        "hand": "手", "hands": "手", "foot": "脚", "feet": "脚",
        "mouth": "嘴", "teeth": "牙齿", "tongue": "舌头", "lips": "嘴唇",
        "thigh": "大腿", "thighs": "大腿", "leg": "腿", "legs": "腿",
        "arm": "手臂", "arms": "手臂", "knee": "膝盖", "knees": "膝盖",
        "shoulder": "肩膀", "neck": "脖子", "head": "头部", "face": "脸",
        "chest": "胸部", "breast": "乳房", "breasts": "乳房",
        "stomach": "腹部", "belly": "肚子", "back": "背部", "hip": "臀部",
        "hips": "臀部", "butt": "屁股", "rear": "臀部", "groin": "胯部",
        "penis": "阴茎", "vagina": "阴道", "anus": "肛门", "ear": "耳朵",
        "ears": "耳朵", "tail": "尾巴", "wing": "翅膀", "wings": "翅膀",
        "claw": "爪子", "claws": "爪子", "paw": "爪", "paws": "爪",
        "hoof": "蹄", "hoofs": "蹄", "horn": "角", "horns": "角"
    });

    /* 咖啡厅食物 */
    st.CAFE_FOOD_CN = mk({
        "coffee": "咖啡", "tea": "茶", "hot chocolate": "热巧克力",
        "milkshake": "奶昔", "smoothie": "冰沙", "cake": "蛋糕",
        "bun": "小圆面包", "cream bun": "奶油面包",
        "deluxe cream bun": "豪华奶油面包", "sandwich": "三明治",
        "scone": "司康", "toast": "吐司", "salad": "沙拉", "soup": "汤",
        "pastry": "糕点", "cookie": "饼干", "muffin": "玛芬",
        "croissant": "可颂", "biscuit": "饼干", "pie": "派"
    });

    /* 方向 */
    st.DirectionCN = mk({
        "north": "北", "south": "南", "east": "东", "west": "西",
        "northeast": "东北", "northwest": "西北",
        "southeast": "东南", "southwest": "西南",
        "up": "上", "down": "下", "left": "左", "right": "右",
        "forward": "前", "backward": "后", "behind": "后面",
        "ahead": "前面", "above": "上方", "below": "下方"
    });

    /* 性玩具 */
    st.NPC_CN_TOOLNAME = mk({
        "dildo": "假阳具", "vibrator": "振动棒", "plug": "肛塞",
        "butt plug": "肛塞", "anal beads": "肛珠", "strap-on": "穿戴式阳具",
        "strapon": "穿戴式阳具", "whip": "鞭子", "crop": "马鞭",
        "paddle": "拍板", "collar": "项圈", "leash": "牵引绳",
        "cuffs": "手铐", "rope": "绳索", "gag": "口塞", "blindfold": "眼罩",
        "clamp": "夹子", "clamps": "夹子", "ring": "环", "cage": "笼",
        "chastity cage": "贞操笼", "wand": "按摩棒", "egg": "蛋"
    });

    /* 妓院演出类型 */
    st.brothelshowType_CN = mk({
        "striptease": "脱衣舞", "strip": "脱衣舞", "dance": "舞蹈",
        "lapdance": "大腿舞", "lap dance": "大腿舞", "pole": "钢管舞",
        "pole dance": "钢管舞", "show": "表演", "performance": "表演",
        "peep": "窥视秀", "peepshow": "窥视秀", "glory": " glory hole",
        "gloryhole": " glory hole", "bdsm": "BDSM 表演",
        "bondage": "捆绑表演", "fetish": "恋物表演"
    });

    /* 衣物名 */
    st.update_cloth_cn = mk(null, function (s) {
        // 常见衣物
        var m = { "shirt": "衬衫", "t-shirt": "T恤", "tshirt": "T恤",
                  "dress": "连衣裙", "skirt": "裙子", "jeans": "牛仔裤",
                  "trousers": "长裤", "pants": "裤子", "shorts": "短裤",
                  "bra": "胸罩", "panties": "内裤", "underwear": "内衣",
                  "socks": "袜子", "stockings": "丝袜", "tights": "连裤袜",
                  "shoes": "鞋子", "boots": "靴子", "heels": "高跟鞋",
                  "jacket": "夹克", "coat": "外套", "hoodie": "连帽衫",
                  "sweater": "毛衣", "blouse": "女式衬衫", "vest": "背心",
                  "apron": "围裙", "uniform": "制服", "costume": "服装" };
        var k = s.toLowerCase().trim();
        if (Object.prototype.hasOwnProperty.call(m, k)) return m[k];
        return s;
    });

    /* setup.T：i18n 用 setup.T.npcClothesItems["lower"][name].desc 之类 */
    if (!st.T || typeof st.T !== "object") st.T = {};
    if (!st.T.npcClothesItems) st.T.npcClothesItems = { upper: {}, lower: {}, under_upper: {}, under_lower: {}, head: {}, neck: {}, hands: {}, feet: {}, legs: {}, genitals: {}, face: {}, over_upper: {}, over_lower: {} };
    ["upper", "lower", "under_upper", "under_lower", "head", "neck", "hands",
     "feet", "legs", "genitals", "face", "over_upper", "over_lower"].forEach(function (k) {
        if (!st.T.npcClothesItems[k]) st.T.npcClothesItems[k] = {};
    });
})();
<</script>>
'''


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")

    if "st.__i18nHelpersInstalled" in data:
        print("（已存在，跳过）")
        return 0

    # 插在 variablesStatic widget 闭合之后
    VS_OPEN = '&lt;&lt;widget "variablesStatic"&gt;&gt;'
    VS_CLOSE = '&lt;&lt;/widget&gt;&gt;'
    i = data.find(VS_OPEN)
    if i < 0:
        print("❌ 找不到 variablesStatic")
        return 1
    j = data.find(VS_CLOSE, i) + len(VS_CLOSE)

    e_block = H.escape(BLOCK, quote=False)
    data = data[:j] + "\n" + e_block + data[j:]
    print("✅ 已插入 i18n 辅助函数")

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")

    # 校验
    g = H.unescape(data)
    print("\n=== 校验 ===")
    for fn in ["BODYPARTS_CN_NAME", "CAFE_FOOD_CN", "DirectionCN", "NPC_CN_TOOLNAME",
               "brothelshowType_CN", "update_cloth_cn"]:
        print(f"  setup.{fn}: {'✅' if ('st.' + fn + ' =') in g else '❌'}")
    print(f"  setup.T: {'✅' if 'st.T.npcClothesItems' in g else '❌'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
