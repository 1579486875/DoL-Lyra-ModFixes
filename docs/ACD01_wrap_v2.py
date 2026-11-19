"""改进包装器：持续监控，模组覆盖后自动重新包装。"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

BLOCK = '''<<script>>
(function () {
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

    var NAMES = ["NPC_CN_TYPE", "NPC_CN_NAME", "NPC_CN_TITLE"];

    function wrapOne(st, name) {
        var orig = st[name];
        if (typeof orig !== "function" || orig.__wrapped) return false;
        var wrapped = function (x) {
            var r;
            try { r = orig(x); } catch (e) { r = x; }
            if (r !== undefined && r !== null && String(r) !== String(x)) return r;
            var k = (x === null || x === undefined) ? "" : String(x).toLowerCase().trim();
            if (Object.prototype.hasOwnProperty.call(EXTRA, k)) return EXTRA[k];
            return (r === undefined || r === null) ? x : r;
        };
        wrapped.__wrapped = true;
        st[name] = wrapped;
        return true;
    }

    function install() {
        var st = window.setup;
        if (!st) return 0;
        var n = 0;
        for (var i = 0; i < NAMES.length; i++) {
            if (wrapOne(st, NAMES[i])) n++;
        }
        if (n) {
            st.__cnWrapCount = (st.__cnWrapCount || 0) + n;
        }
        if (!st.__cnTypeLookup) {
            st.__cnTypeLookup = function (x) {
                var k = String(x || "").toLowerCase().trim();
                return EXTRA[k] || null;
            };
        }
        return n;
    }

    /* 持续监控：每 1.5 秒检查一次，最多 120 次（3 分钟） */
    var cnt = 0;
    var timer = setInterval(function () {
        cnt++;
        install();
        if (cnt > 120) clearInterval(timer);
    }, 1500);

    /* 事件触发也装 */
    if (window.jQuery) {
        jQuery(document).on(":storyready :passagedisplay :passageinit", function () {
            setTimeout(install, 100);
            setTimeout(install, 1200);
            setTimeout(install, 4000);
        });
    }
    setTimeout(install, 2000);
    setTimeout(install, 6000);
    setTimeout(install, 12000);
    setTimeout(install, 25000);
})();
<</script>>
'''


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")

    # 删掉旧版（含 __cnTypePatched 的块）
    old_pat_esc = re.compile(
        r"&lt;&lt;script&gt;&gt;\s*\(function \(\) \{\s*/\* 等模组全部加载完再包装.*?&lt;&lt;/script&gt;&gt;", re.S)
    old_pat_raw = re.compile(
        r"<<script>>\s*\(function \(\) \{\s*/\* 等模组全部加载完再包装.*?<</script>>", re.S)
    n_removed = 0
    while old_pat_esc.search(data):
        data = old_pat_esc.sub("", data, 1)
        n_removed += 1
    while old_pat_raw.search(data):
        data = old_pat_raw.sub("", data, 1)
        n_removed += 1
    if n_removed:
        print(f"  已移除旧版 {n_removed} 处")

    VS_OPEN = '&lt;&lt;widget "variablesStatic"&gt;&gt;'
    VS_CLOSE = '&lt;&lt;/widget&gt;&gt;'
    i = data.find(VS_OPEN)
    if i < 0:
        print("❌ 找不到 variablesStatic")
        return 1
    j = data.find(VS_CLOSE, i) + len(VS_CLOSE)

    e_block = H.escape(BLOCK, quote=False)
    data = data[:j] + "\n" + e_block + data[j:]
    print("✅ 已插入持续监控版包装器")

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
