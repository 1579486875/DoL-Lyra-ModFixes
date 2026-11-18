import html, json, os, re

HTML = r"E:\TAML\_dol\work\index_modded6.html"
PAIRS = r"E:\TAML\_dol\work\i18n_varstatic_safe.json"

pairs = json.load(open(PAIRS, "r", encoding="utf-8"))
print("待注入:", len(pairs))

data = open(HTML, "rb").read()
g = data.decode("utf-8", "replace")

# 定位 Widgets variablesStatic passage
m = re.search(r'(<tw-passagedata[^>]*name="Widgets variablesStatic"[^>]*>)(.*?)(</tw-passagedata>)', g, re.S)
if not m:
    print("❌ passage 未找到")
    raise SystemExit(1)

body = m.group(2)
print("passage 长度:", len(body))

applied = 0
missed = []
for f, t in pairs:
    # 转义（passage 在 HTML 里被转义过）
    fe = html.escape(f, quote=False)
    te = html.escape(t, quote=False)
    if fe in body:
        body = body.replace(fe, te, 1)
        applied += 1
    elif f in body:
        body = body.replace(f, t, 1)
        applied += 1
    else:
        missed.append(f[:70])

print(f"注入成功: {applied}")
print(f"未命中: {len(missed)}")
for x in missed[:10]:
    print("   ", repr(x))

new_g = g[:m.start(2)] + body + g[m.end(2):]
open(HTML, "wb").write(new_g.encode("utf-8"))
print(f"\n写出: {HTML}  ({os.path.getsize(HTML):,} 字节)")
