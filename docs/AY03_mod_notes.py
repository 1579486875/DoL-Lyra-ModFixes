"""AY03（第14轮）：给本包修补过的第三方模组写上「修补说明」（幂等，模板 §7.4「同步更新模组描述」）。

这些模组原本没有 description 字段，ModLoader 会忽略未知字段，加上不影响加载；
版本号保持原作者的不变（其它模组的 dependenceInfo 可能按版本号检查）。
说明写进 description，并另存一份结构化的 modFixesNotes 列表，方便以后追溯。
"""
import json
import os
import re
import sys

sys.path.insert(0, r"E:\TAML\_dol\work")
import modzip_lib as MZ

HTML = os.environ.get("DOL_HTML") or r"E:\TAML\_dol\work\index_modded6.html"
data = open(HTML, "rb").read().decode("utf-8", "replace")
if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[AY03] index 形态异常")
    sys.exit(1)

PREFIX = "【DoL-Lyra-ModFixes 修补说明】"
NOTES = {
    "DoLSims": [
        "第12轮 AR02：fallenTransform 补丁（书本特性保护光环）的锚点兼容 maplebirch 5.6.2 在 widget 开头加的 <<if not …>>，并用 $1 保留其开标签。",
    ],
    "DomRobin": [
        "第12轮 AR02：罗宾自付债务（贝利办公室 / robinpay）两处锚点兼容 maplebirch 追加的 orphanage.*Free 条件；"
        "海风咖啡馆买酒选项的锚点兼容 maplebirch.get(\"Finance\").canPay(300, \"cafe\") 新 API。",
    ],
    "Wraith'sReflection": [
        "第12轮 AF01：SilverConchTalk.twee 里 5 处 <<set _chat.push(\"…\")>> 的双引号字符串跨行（eval 时 SyntaxError，"
        "银海螺永远没有对话），只把字符串内部的换行+缩进折叠成空格，文本与 <br> 原样保留。",
    ],
    "ModI18N": [
        "第12轮 AP01：其中 7853 条 JS 译文已在构建期按 ModI18N 同款算法烘焙进游戏脚本，并从本包 i18n.json 里删除，"
        "避免运行时二次替换（否则 let group_cn 会被声明两次，游戏无法启动）。passage 译文条目未改动。",
    ],
}
changed_all = []
for mod, notes in NOTES.items():
    def fn(name, b, notes=notes):
        if name != "boot.json":
            return None
        bj = json.loads(b.decode("utf-8-sig"))
        old = list(bj.get("modFixesNotes") or [])
        if all(n in old for n in notes):
            return None
        bj["modFixesNotes"] = old + [n for n in notes if n not in old]
        desc = bj.get("description") or ""
        if PREFIX in desc:
            desc = desc[:desc.index(PREFIX)].rstrip()
        bj["description"] = (desc + " " if desc else "") + PREFIX + " ".join(bj["modFixesNotes"])
        return json.dumps(bj, ensure_ascii=False, indent=2).encode("utf-8")

    data, ch = MZ.patch_mod(data, mod, fn)
    if ch:
        changed_all.append(mod)
if changed_all:
    open(HTML, "wb").write(data.encode("utf-8"))
print("[AY03] 写入修补说明: %s" % (changed_all or "无变化（已存在）"))
