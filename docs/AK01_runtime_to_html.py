"""AK01：把 cdp_suite 导出的运行时 passage（jsonl）转成伪 index.html，让静态工具（T03/scan_lib）能直接复查运行时真实文本。

运行时文本 = 原 index 经 ModI18N 运行时替换、TweeReplacer/ReplacePatcher 补丁、各模组 twee 合并之后的样子。
引擎源码段取自 vanilla index.html（T03 需要从中抠出 Scripting.parse）。
"""
import html as H
import json
import sys

src = sys.argv[1] if len(sys.argv) > 1 else r"E:\TAML\_dol\work\_runtime_passages.jsonl"
out = sys.argv[2] if len(sys.argv) > 2 else r"E:\TAML\_dol\work\_runtime_index.html"
van = open(r"E:\TAML\_dol\work\index.html", "rb").read().decode("utf-8", "replace")
cut = van.find("<tw-storydata")
end = van.find("</tw-storydata>", cut) + len("</tw-storydata>")
head = van[:cut]
tail = van[end:]          # 引擎（含 Scripting.parse）位于 storydata 之后
parts = [head, '<tw-storydata name="runtime">\n']
n = 0
for line in open(src, encoding="utf-8"):
    if not line.strip():
        continue
    title, tags, text = json.loads(line)
    parts.append('<tw-passagedata pid="%d" name="%s" tags="%s">%s</tw-passagedata>\n' % (
        n + 1, H.escape(title, quote=True), H.escape(tags, quote=True), H.escape(text, quote=False)))
    n += 1
parts.append("</tw-storydata>")
parts.append(tail)
open(out, "w", encoding="utf-8").write("".join(parts))
print("运行时 passage %d 个 → %s" % (n, out))
