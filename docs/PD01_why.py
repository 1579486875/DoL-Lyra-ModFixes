"""查为什么 i18n 的 Pain: -> 疼痛：没被 BE_bake 应用。"""
import json
import re

HTML = r"E:\TAML\_dol\work\index_modded6.html"
I18N = r"E:\TAML\_dol\work\i18n_dict.json"

raw = open(HTML, "rb").read().decode("utf-8", "replace")
import html as H
g = H.unescape(raw)

# 取 Widgets passage
m = re.search(r'<tw-passagedata[^>]*name="Widgets"[^>]*>(.*?)</tw-passagedata>', raw, re.S)
body = H.unescape(m.group(1)) if m else ""
print(f"Widgets passage 长度: {len(body)}")

d = json.load(open(I18N, "r", encoding="utf-8"))
items = [it for it in d["typeB"]["TypeBInputStoryScript"] if it.get("pN") == "Widgets"]
print(f"i18n 里 Widgets 条目: {len(items)}")

TARGETS = ["Pain:", "Arousal:", "Fatigue:", "Stress:", "Trauma:", "Control:", "Allure:"]
for t in TARGETS:
    it = next((x for x in items if (x.get("f") or "").strip() == t), None)
    if not it:
        print(f"\n{t!r}: i18n 无")
        continue
    f, tr, pos = it["f"], it["t"], it.get("pos", -1)
    exact = 0 <= pos <= len(body) and body[pos:pos + len(f)] == f
    sub = f in body
    cnt = body.count(f)
    print(f"\n{t!r}  pos={pos}  精确={exact}  子串={sub}  出现 {cnt} 次")
    if sub:
        i = body.find(f)
        print(f"     上下文: {body[max(0,i-120):i+80]!r}")

# 检查 _is_code_like 会不会拦
def is_code_like(text):
    if not text:
        return False
    for kw in ("<<widget", "<<macro", "Macro.add"):
        if kw in text:
            return True
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", text) and len(text) <= 40:
        return True
    return False

print("\n=== _is_code_like 判定 ===")
for t in TARGETS:
    print(f"  {t!r}: {is_code_like(t)}")
