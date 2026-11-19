"""NPC_CN_TYPE/NAME/TITLE 兜底包装器：模组版本优先，翻不出来用补充表。

根因：模组（NpcNameCN）在 storyready 时覆盖了 setup.NPC_CN_TYPE，
      它内部的 TITLES 表只有职业/身份词，没有野兽名。
解法：在 :storyready 之后包装，保留模组能力，补上缺失的词。
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

BLOCK = '''<<script>>
(function () {
    /* 等模组全部加载完再包装 */
    function install() {
        if (!window.setup) return;
        var st = window.setup;
        if (st.__cnTypePatched) return;
        st.__cnTypePatched = true;

        /* 补充表：模组 TITLES 里没有的生物/野兽/怪物名 */
        var EXTRA = {
            "human": "人类", "man": "男人", "woman": "女人", "boy": "男孩",
            "girl": "女孩", "male": "男性", "female": "女性",
            "lizard": "蜥蜴", "eels": "鳗鱼", "eel": "鳗鱼",
            "whale": "鲸鱼", "whales": "鲸鱼", "lizards": "蜥蜴",
            "slime": "史莱姆", "slimes": "史莱姆",
            "worm": "蠕虫", "worms": "蠕虫",
            "spider": "蜘蛛", "spiders": "蜘蛛",
            "maggot": "蛆虫", "maggots": "蛆虫",
            "wasp": "黄蜂", "wasps": "黄蜂",
            "bee": "蜜蜂", "bees": "蜜蜂",
            "squid": "鱿鱼", "squids": "鱿鱼",
            "vine": "藤蔓", "vines": "藤蔓",
            "slug": "蛞蝓", "slugs": "蛞蝓",
            "tentacle": "触手", "tentacles": "触手",
            "lurker": "潜伏者", "lurkers": "潜伏者",
            "fish": "鱼", "snake": "蛇", "snakes": "蛇",
            "wolf": "狼", "wolves": "狼", "bear": "熊", "bears": "熊",
            "elk": "麋鹿", "seal": "海豹", "dolphin": "海豚",
            "octopus": "章鱼", "chimp": "猩猩", "monkey": "猴子",
            "baboon": "狒狒", "tiger": "老虎", "lion": "狮子",
            "leopard": "豹", "cheetah": "猎豹", "panther": "黑豹",
            "cat": "猫", "cats": "猫", "dog": "狗", "dogs": "狗",
            "boar": "野猪", "rabbit": "兔子", "rat": "老鼠",
            "mouse": "老鼠", "bat": "蝙蝠", "crow": "乌鸦",
            "hawk": "鹰", "eagle": "雕", "owl": "猫头鹰",
            "horse": "马", "horses": "马", "cow": "牛", "cows": "牛",
            "sheep": "羊", "goat": "山羊", "pig": "猪", "chicken": "鸡",
            "frog": "青蛙", "toad": "蟾蜍", "beast": "野兽",
            "monster": "怪物", "plant": "植物", "plantperson": "植物人",
            "great hawk": "巨鹰", "black wolf": "黑狼",
            "ivory wraith": "象牙幽灵", "night monster": "夜魔",
            "tentacle beast": "触手兽", "swarm": "虫群",
            "insect": "昆虫", "insects": "昆虫",
            "abomination": "憎恶", "ghost": "幽灵"
        };

        function wrap(fnName) {
            var orig = st[fnName];
            if (typeof orig !== "function") return;
            if (orig.__wrapped) return;
            var wrapped = function (x) {
                var r;
                try { r = orig(x); } catch (e) { r = x; }
                /* 原函数翻出来了（结果变了且非空），直接返回 */
                if (r !== undefined && r !== null && String(r) !== String(x)) return r;
                /* 原函数翻不出来，用补充表 */
                var k = (x === null || x === undefined) ? "" : String(x).toLowerCase().trim();
                if (Object.prototype.hasOwnProperty.call(EXTRA, k)) return EXTRA[k];
                return (r === undefined || r === null) ? x : r;
            };
            wrapped.__wrapped = true;
            st[fnName] = wrapped;
        }

        wrap("NPC_CN_TYPE");
        wrap("NPC_CN_NAME");
        wrap("NPC_CN_TITLE");

        /* 同时暴露一个直接查询函数，供调试 */
        st.__cnTypeLookup = function (x) {
            var k = String(x || "").toLowerCase().trim();
            return EXTRA[k] || null;
        };
    }

    /* 多个时机尝试，确保模组已加载 */
    if (window.jQuery) {
        jQuery(document).one(":storyready", function () { setTimeout(install, 500); });
        jQuery(document).on(":passagedisplay", function () { if (!window.setup || !window.setup.__cnTypePatched) install(); });
    }
    setTimeout(install, 3000);
    setTimeout(install, 8000);
    setTimeout(install, 15000);
})();
<</script>>
'''


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")

    if "__cnTypePatched" in data:
        print("（已存在，先移除旧的）")
        data = re.sub(
            r"&lt;&lt;script&gt;&gt;\s*\(function \(\) \{\s*/\* 等模组全部加载完再包装.*?&lt;&lt;/script&gt;&gt;",
            "", data, flags=re.S)
        data = re.sub(
            r"<<script>>\s*\(function \(\) \{\s*/\* 等模组全部加载完再包装.*?<</script>>",
            "", data, flags=re.S)

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
    print("✅ 已插入 NPC_CN_* 兜底包装器")

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")

    g = H.unescape(data)
    print("\n=== 校验 ===")
    print(f"  __cnTypePatched: {'✅' if '__cnTypePatched' in g else '❌'}")
    print(f"  EXTRA 表: {'✅' if 'lizard' in g and '蜥蜴' in g else '❌'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
