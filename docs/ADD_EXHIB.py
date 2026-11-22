# -*- coding: utf-8 -*-
import base64
import re
import sys

HTML = r"E:\TAML\_dol\work\index_modded6.html"
P = r"E:\TAML\_dol\work\_downloads\MyExhibitionismExpansion-1.0.4-DolMod.zip"

raw = open(HTML, "rb").read().decode("utf-8", "replace")
npass = len(re.findall(r'<tw-passagedata[^>]*name="', raw))
m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw, re.S)
block = m.group(1)
b64 = base64.b64encode(open(P, "rb").read()).decode("ascii")
if b64 in block:
    print("already")
    sys.exit(0)
block = block.rstrip()
if not block.endswith(","):
    block += ","
block += '\n"' + b64 + '"'
raw2 = raw[:m.start(1)] + block + raw[m.end(1):]
npass2 = len(re.findall(r'<tw-passagedata[^>]*name="', raw2))
m2 = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", raw2, re.S)
cnt = len(re.findall(r'"[A-Za-z0-9+/=\s]{200,}"', m2.group(1)))
print("passage", npass, "->", npass2, "| mods", cnt)
if npass2 != npass:
    print("❌ passage 变化")
    sys.exit(1)
open(HTML, "wb").write(raw2.encode("utf-8"))
print("written", len(raw2))
