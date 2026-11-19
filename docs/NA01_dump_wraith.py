import html
import re

HTML = r"E:\TAML\_dol\work\index_modded6.html"
g = html.unescape(open(HTML, "rb").read().decode("utf-8", "replace"))

i = g.find("_speechWraith")
print("=== _speechWraith 全部出现 ===")
for m in re.finditer("_speechWraith", g):
    print(f"\n@{m.start()}")
    print(repr(g[max(0, m.start() - 350):m.start() + 400]))
