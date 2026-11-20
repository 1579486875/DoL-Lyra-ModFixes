"""T19：扫模组 JS 里硬编码的 UI 文本（玩家可见）。

重点抓这些形态：
  text: "英文"
  label: "英文"
  innerHTML = "英文"
  .textContent = "英文"
  name: "英文"
  placeholder: "英文"
  title: "英文"
  hint: "英文"
  + "英文"  (拼接进 UI)
"""
import base64
import html as H
import io
import json
import re
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
g = H.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))

SKIP = {"ModI18N", "ModLoaderGui", "ModLoader", "TweeReplacer", "I18nTweeReplacer",
        "TweeReplacerLinker", "ModSubUiAngularJs", "MapleBirchCE", "ImageLoader"}

m = re.search(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", g, re.S)
parts = re.findall(r'"([A-Za-z0-9+/=\s]{200,})"', m.group(1))

# UI 文本字段名
FIELDS = ("text", "label", "title", "hint", "placeholder", "name", "desc",
          "description", "tooltip", "message", "caption", "header", "button",
          "innerHTML", "textContent", "innerText")

PAT = re.compile(
    r'\b(?:' + "|".join(FIELDS) + r')\s*[:=]\s*["\'`]([^"\'`]{6,150})["\'`]'
)


def is_ui_text(s):
    if re.search(r"[\u4e00-\u9fff]", s):
        return False
    if len(re.findall(r"[A-Za-z]{2,}", s)) < 2:
        return False
    if re.search(r"[$`]|=>|\bfunction\b|\bvar\b|\bconst\b|\breturn\b|\bnull\b|\bundefined\b", s):
        return False
    # 排除类名/路径/ID
    if re.fullmatch(r"[a-z0-9_\-./]+", s):
        return False
    if re.search(r"\.(png|jpg|gif|css|js|twee|json)$", s, re.I):
        return False
    # 排除 camelCase / snake_case 标识符
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", s):
        return False
    return True


results = {}
for s in parts:
    raw = base64.b64decode(re.sub(r"\s+", "", s))
    if raw[:2] != b"PK":
        continue
    try:
        zz = zipfile.ZipFile(io.BytesIO(raw))
        bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
        modname = bj.get("name", "?")
    except Exception:
        continue
    if modname in SKIP:
        continue

    hits = []
    for n in zz.namelist():
        if not n.endswith((".js", ".twee")):
            continue
        try:
            txt = zz.read(n).decode("utf-8", "replace")
        except Exception:
            continue
        for mm in PAT.finditer(txt):
            v = mm.group(1)
            if is_ui_text(v):
                hits.append((n, mm.group(0)[:40], v[:110]))
    if hits:
        results[modname] = hits

print("=" * 95)
print(f"模组 JS 里疑似 UI 英文：{len(results)} 个模组")
print("=" * 95)

total = 0
for mod, hits in sorted(results.items(), key=lambda x: -len(x[1])):
    total += len(hits)
    print(f"\n[{mod}]  {len(hits)} 条")
    seen = set()
    shown = 0
    for n, ctx, v in hits:
        if v in seen:
            continue
        seen.add(v)
        print(f"    {v!r}")
        shown += 1
        if shown >= 10:
            if len(hits) > shown:
                print(f"    ... 共 {len(hits)} 条（去重 {len(seen)}）")
            break

print("\n" + "=" * 95)
print(f"总计 {total} 条，跨 {len(results)} 个模组")
print("=" * 95)

with open(r"E:\TAML\_dol\work\_mod_js_ui_en.json", "w", encoding="utf-8") as f:
    json.dump({k: sorted(set(v[2] for v in vals))[:80] for k, vals in results.items()},
              f, ensure_ascii=False, indent=1)
print("已保存 _mod_js_ui_en.json")
