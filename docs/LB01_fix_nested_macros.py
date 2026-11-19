"""紧急修复（精确版）。

问题一（致命，导致 relation-box / social 全挂）：
  relation-box 里唯一一处
    <<if (<<NPC_CN_NAME <<NPC_CN_NAME <<NPC_CN_NAME _npcData.nam>>>>>> is ("Ivory Wraith") or ...
  应为
    <<if (_npcData.nam is ("Ivory Wraith") or ...

  原因：i18n 的 t 把 `_npcData.nam` 换成 `<<NPC_CN_NAME _npcData.nam>>`，
        BE_bake 对同一 passage 反复应用，在已替换的文本上又套了两层。
  SugarCube 的 <<if>> 是纯 JS 表达式，不能含 `<<` → SyntaxError。

问题二：NPC_CN_NAME / NPC_CN_TYPE / BODYPARTS_CN_NAME 宏与 setup.* 函数
        在 index 里一个定义都没有（只存在于模组 JS，且未注册成功）
        → Bedroom 里刷屏 "macro <<NPC_CN_NAME>> does not exist"

修法：
  1) 精确折叠那 1 处嵌套（不做全局正则，避免误伤）
  2) 在 relation-box 定义之前插入 3 个宏 + 4 个 setup 函数
"""
import html as H
import os
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"

BAD_IF = ('<<if (<<NPC_CN_NAME <<NPC_CN_NAME <<NPC_CN_NAME _npcData.nam>>>>>> '
          'is ("Ivory Wraith")')
GOOD_IF = '<<if (_npcData.nam is ("Ivory Wraith")'

DEFS = r'''<<widget "NPC_CN_NAME">><<= (setup.NPC_CN_NAME ? setup.NPC_CN_NAME(_args[0]) : _args[0])>><</widget>>
<<widget "NPC_CN_TYPE">><<= (setup.NPC_CN_TYPE ? setup.NPC_CN_TYPE(_args[0]) : _args[0])>><</widget>>
<<widget "BODYPARTS_CN_NAME">><<= (setup.BODYPARTS_CN_NAME ? setup.BODYPARTS_CN_NAME(_args[0]) : _args[0])>><</widget>>
<<script>>
(function () {
    if (!window.SugarCube || !SugarCube.setup) return;
    var st = SugarCube.setup;
    if (st.__cnTablesInstalled) return;
    st.__cnTablesInstalled = true;

    function parseTable(raw) {
        var out = {};
        if (!raw || typeof raw !== "string") return out;
        raw.split("|").forEach(function (pair) {
            var i = pair.indexOf(",");
            if (i < 0) return;
            var k = pair.slice(0, i).trim();
            var v = pair.slice(i + 1).trim();
            if (k && v) out[k.toLowerCase()] = v;
        });
        return out;
    }

    var typeMap = null, nameMap = null;

    function typeTable() {
        if (typeMap === null) typeMap = parseTable(st.NPCTypeList_cn_name);
        return typeMap;
    }
    function nameTable() {
        if (nameMap === null) nameMap = parseTable(st.NPCNameList_cn_name);
        return nameMap;
    }

    var PART = {
        "left hand": "左手", "right hand": "右手", "hand": "手", "hands": "双手",
        "left arm": "左臂", "right arm": "右臂", "arm": "手臂", "arms": "双臂",
        "left leg": "左腿", "right leg": "右腿", "leg": "腿", "legs": "双腿",
        "foot": "脚", "feet": "双脚", "mouth": "嘴", "tongue": "舌头",
        "penis": "肉棒", "vagina": "阴部", "anus": "肛门", "ass": "屁股",
        "breasts": "胸部", "breast": "胸部", "nipple": "乳头", "nipples": "乳头",
        "buttocks": "臀部", "bottom": "臀部", "thigh": "大腿", "thighs": "大腿",
        "tail": "尾巴", "wings": "翅膀", "horn": "角", "horns": "角",
        "ears": "耳朵", "ear": "耳朵", "tentacle": "触手", "tentacles": "触手",
        "head": "头", "neck": "脖子", "chest": "胸口", "tummy": "肚子",
        "face": "脸", "hair": "头发", "hips": "腰胯", "waist": "腰",
        "genitals": "生殖器", "teeth": "牙齿", "lips": "嘴唇"
    };

    function look(map, key) {
        if (!key || typeof key !== "string") return key;
        var v = map[key.toLowerCase()];
        return v === undefined ? key : v;
    }

    /* 只 return，绝不给入参赋值 —— 旧 shim 就是在这一步污染了 _parasiteTypes */
    st.NPC_CN_TYPE = function (x) { return look(typeTable(), x); };
    st.NPC_CN_NAME = function (x) { return look(nameTable(), x); };
    st.NPC_CN_TITLE = function (x) { return look(typeTable(), x); };
    st.BODYPARTS_CN_NAME = function (x) { return look(PART, x); };
})();
<</script>>
'''


def main():
    data = open(HTML, "rb").read().decode("utf-8", "replace")

    # ---- 1) 精确折叠 ----
    e_bad = H.escape(BAD_IF, quote=False)
    e_good = H.escape(GOOD_IF, quote=False)
    if e_bad in data:
        data = data.replace(e_bad, e_good, 1)
        print("✅ 已修复关系框里的嵌套宏（转义形态）")
    elif BAD_IF in data:
        data = data.replace(BAD_IF, GOOD_IF, 1)
        print("✅ 已修复关系框里的嵌套宏（未转义）")
    else:
        print("⚠️  未找到目标嵌套（可能已修）")

    # ---- 2) 插入定义 ----
    if '&lt;&lt;widget "NPC_CN_NAME"' in data or '<<widget "NPC_CN_NAME"' in data:
        print("（宏定义已存在）")
    else:
        anchor = '&lt;&lt;widget "relation-box"&gt;&gt;'
        if anchor in data:
            data = data.replace(anchor, H.escape(DEFS, quote=False) + anchor, 1)
            print("✅ 已在 relation-box 之前插入宏与函数定义（转义形态）")
        else:
            anchor2 = '<<widget "relation-box">>'
            if anchor2 in data:
                data = data.replace(anchor2, DEFS + anchor2, 1)
                print("✅ 已在 relation-box 之前插入宏与函数定义")
            else:
                print("❌ 找不到插入锚点")
                return 1

    open(HTML, "wb").write(data.encode("utf-8"))
    print(f"\n写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")

    # ---- 校验 ----
    g = H.unescape(data)
    print("\n=== 校验 ===")
    for kw in ("NPC_CN_NAME", "NPC_CN_TYPE", "BODYPARTS_CN_NAME"):
        n = len(re.findall(r'<<widget "' + kw + r'"', g))
        print(f"  {kw:<20} 宏定义 {n}")
    print(f"  嵌套残留: {g.count('<<NPC_CN_NAME <<NPC_CN_NAME')}")
    print(f"  <<if>> 里含 << : {len(re.findall(chr(60)*2 + 'if[^>]{0,80}' + chr(60)*2, g))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
