"""补两个缺失的符号：
  1) setup.description_CN 函数（i18n 引用了但没提供）
  2) <<wTimerProgress>> widget（报 does not exist，补一份到最早注册的位置）

插入位置：variablesStatic widget 的闭合标签之后（passage 级别）。
绝不能插在 bodyShapes 后面 —— 那在 widget 内部，会造成 widget 嵌套。
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

# 锚点：bodyShapes 那一行
ANCHOR = '<<set setup.bodyShapes to ["classic", "slender", "curvy", "soft"]>>'

DEFS = '''<<widget "wTimerProgress">><<if $wraith and $wraith.state and $wraith.hunt is 0 and typeof Time !== "undefined" and Time.isBloodMoon()>><<set $wraith.timer to ($wraith.timer || 0) + 1>><<set $wraith.timer to $wraith.timer + Math.floor((C.npc["Ivory Wraith"] && C.npc["Ivory Wraith"].lust || 0) / 10)>><<if $rng gte 61 and typeof numberOfEarSlime === "function" and numberOfEarSlime()>><<set $wraith.timer to $wraith.timer + 1>><</if>><</if>><</widget>>
<<script>>
(function () {
    if (!window.SugarCube || !SugarCube.setup) return;
    var st = SugarCube.setup;
    if (st.__descCNInstalled) return;
    st.__descCNInstalled = true;

    /* setup.description_CN(x)：把 NPC 外观描述词翻成中文。
       查不到就返回原值 —— 绝不让它抛错。 */
    var _DESC = {
        "tall": "高挑", "short": "矮小", "average": "中等",
        "thin": "瘦削", "slim": "纤细", "slender": "苗条",
        "curvy": "曲线玲珑", "plump": "丰满", "chubby": "圆润",
        "muscular": "健壮", "toned": "结实", "athletic": "健美",
        "fat": "肥胖", "skinny": "骨感", "stocky": "敦实",
        "young": "年轻", "old": "年长", "mature": "成熟",
        "handsome": "英俊", "pretty": "漂亮", "beautiful": "美丽",
        "cute": "可爱", "plain": "普通", "ugly": "丑陋",
        "pale": "苍白", "tan": "古铜", "dark": "深色", "light": "浅色",
        "freckled": "有雀斑", "scarred": "有疤痕", "clean": "干净",
        "dirty": "脏兮兮", "scruffy": "邋遢", "neat": "整洁",
        "blond": "金发", "blonde": "金发", "brunette": "棕发",
        "redhead": "红发", "black": "黑发", "brown": "棕发",
        "white": "白发", "grey": "灰发", "ginger": "姜红发",
        "bald": "秃顶", "long": "长", "medium": "中等", "short_hair": "短发",
        "boy": "男孩", "girl": "女孩", "man": "男人", "woman": "女人",
        "male": "男性", "female": "女性", "adult": "成年人",
        "student": "学生", "worker": "工人", "teacher": "教师"
    };

    function descCN(x) {
        if (x === null || x === undefined) return "";
        var s = String(x);
        var key = s.toLowerCase().trim();
        if (Object.prototype.hasOwnProperty.call(_DESC, key)) return _DESC[key];
        // 复合词：按 _ 或空格拆开逐个译
        if (/[_\s]/.test(s)) {
            return s.split(/[_\s]+/).map(function (p) {
                var k2 = p.toLowerCase();
                return Object.prototype.hasOwnProperty.call(_DESC, k2) ? _DESC[k2] : p;
            }).join("");
        }
        return s;
    }

    st.description_CN = descCN;
})();
<</script>>
'''

# 也补一个 descriptionCN（有些地方可能用驼峰）
DEFS += '<<script>>(function(){if(!window.SugarCube||!SugarCube.setup)return;var s=SugarCube.setup;if(!s.descriptionCN)s.descriptionCN=s.description_CN;})();<</script>>\n'


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")

    # 已有就不重复插
    if 'setup.__descCNInstalled' in data and '<<widget "wTimerProgress">><<if $wraith' in data:
        print("（已存在，跳过）")
        return 0

    e_defs = H.escape(DEFS, quote=False)

    # 新锚点：variablesStatic widget 的闭合标签（passage 级别，不在任何 widget 内）
    VS_OPEN = '&lt;&lt;widget "variablesStatic"&gt;&gt;'
    VS_CLOSE = '&lt;&lt;/widget&gt;&gt;'
    i = data.find(VS_OPEN)
    if i < 0:
        print("❌ 找不到 variablesStatic")
        return 1
    j = data.find(VS_CLOSE, i)
    if j < 0:
        print("❌ 找不到 variablesStatic 的闭合")
        return 1
    j += len(VS_CLOSE)
    data = data[:j] + "\n" + e_defs + data[j:]
    print("✅ 已插到 variablesStatic 之后（passage 级别，不会造成 widget 嵌套）")

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")

    g = H.unescape(data)
    print("\n=== 校验 ===")
    print(f"  wTimerProgress widget: {len(re.findall(chr(60)*2 + 'widget \"wTimerProgress\"', g))}")
    print(f"  setup.description_CN 赋值: {len(re.findall(r'st\\.description_CN\\s*=', g))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
