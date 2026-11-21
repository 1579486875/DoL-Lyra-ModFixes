"""AP01（第12轮）：构建期把 ModI18N 官方 JS/CSS 译文「烘焙」进 index（幂等）。

为什么要做（第12轮运行时实测）：
  ModI18N 在运行时按 (fileName, pos, from→to) 替换游戏 JS；匹配窗口只有 pos-10 ~ pos+len+30。
  我们后续的静态翻译脚本（AC06 成就名 / AB06~AB13 JS 文本 / P05~T10 模板等）一旦改了某个 JS 文件
  前部的文字长度，同文件后面的官方条目全部错位失配 —— 运行时实测：
    · 成就描述 299 条里只剩 47 条中文、提示 152 条只剩 2 条中文（基线包是 299/299、152/152）
    · 官方译文被我们的自译覆盖（如 Pocket Change 官方「第一桶金」被改成「零钱」）
    · 运行时 JS 替换失败从基线 768 条涨到 2952 条
  烘焙后，静态内容 = 运行时官方翻译结果；我们的自译脚本只会处理官方没覆盖的残余英文。

算法与 ModI18N 1.0.1a 的 ModI18NTypeB_JsCssMatcher 完全一致：
  同一文件的条目按 pos 从大到小处理（替换不影响更靠前的位置）；
  先在 pos, pos-1, pos-2, pos+1, pos+2 做精确比较，再在 [pos-10, pos+len+30] 窗口里找字面量。

★ 烘焙后必须把「已烘焙的条目」从包内 ModI18N 的 i18n.json 里删掉（第12轮实测事故）：
  不少官方条目的译文以原文开头（f="let group;" → t="let group; let group_cn;"），
  烘焙后原文在原位置仍能精确命中，运行时 ModI18N 会再替换一次 →
  `let group_cn` 被声明两次 → 整个用户脚本 SyntaxError → 游戏启动报「C is not defined」致命错误。
  只删 JS 条目（TypeBOutputText 里 js:true 的），passage 条目（TypeBInputStoryScript）不动。
  ModI18N 按模组 ZIP 的哈希做 IndexedDB 缓存键，ZIP 内容一变缓存自动失效，不会读到旧数据。
"""
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, r"E:\TAML\_dol\work")
import modzip_lib as MZ

HTML = os.environ.get("DOL_HTML") or r"E:\TAML\_dol\work\index_modded6.html"
MARK = "/* [AP01] ModI18N official JS translations baked */"

data = open(HTML, "rb").read().decode("utf-8", "replace")
if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[AP01] index 形态异常")
    sys.exit(1)
if MARK in data:
    print("[AP01] 已存在，跳过")
    sys.exit(0)

# 以包内 ModI18N 的 i18n.json 为唯一来源（就是运行时会用的那份）
raw_i18n = MZ.read_mod_file(data, "ModI18N", "i18n.json")
if raw_i18n is None:
    print("[AP01] FAIL 包内找不到 ModI18N/i18n.json")
    sys.exit(1)
d = json.loads(raw_i18n.decode("utf-8-sig"))

buf = defaultdict(list)
# 运行时 ModI18N 只把 TypeBOutputText 里带 js/css 标记的条目用于脚本替换
# （TypeBInputStoryScript 在解析时丢掉了 js 字段，不参与 JS 替换）—— 与之保持一致
for v in d["typeB"].get("TypeBOutputText", []):
    if v.get("fileName") and v.get("js") and isinstance(v.get("f"), str) and isinstance(v.get("t"), str):
        buf[v["fileName"]].append(v)
for k in buf:
    buf[k].sort(key=lambda v: -(v.get("pos") or 0))


def strcmp_offset_ok(s, target, off):
    if off < 0 or off >= len(s):
        return False
    return s.startswith(target, off)


stat = Counter()
fail_detail = defaultdict(int)
baked = set()


def replace_js(s, rep, fname):
    for v in rep:
        f, t, pos = v["f"], v["t"], v.get("pos") or 0
        hit = None
        for off in (pos, pos - 1, pos - 2, pos + 1, pos + 2):
            if strcmp_offset_ok(s, f, off):
                hit = off
                break
        if hit is None:
            st = max(0, pos - 10)
            en = min(len(s), pos + len(f) + 30)
            k = s.find(f, st, en) if en - st >= len(f) else -1
            if k >= 0 and k + len(f) <= en:
                hit = k
        if hit is None:
            stat["fail"] += 1
            fail_detail[fname] += 1
            continue
        s = s[:hit] + t + s[hit + len(f):]
        stat["ok"] += 1
        baked.add((v["fileName"], v.get("pos"), f))
    return s


# ---- 定位 twine-user-script 元素，按头部切分 ----
op = data.find('<script role="script" id="twine-user-script" type="text/twine-javascript">')
if op < 0:
    print("[AP01] FAIL 找不到 twine-user-script")
    sys.exit(1)
cs = op + len('<script role="script" id="twine-user-script" type="text/twine-javascript">')
ce = data.find("</script>", cs)
script = data[cs:ce]
HEAD = re.compile(r'(/\* twine-user-script #)(\d+): "([^\'"]+)" \*/')
parts = HEAD.split(script)
out = [parts[0]]
nfiles = 0
i = 1
while i < len(parts):
    pre, num, name, content = parts[i], parts[i + 1], parts[i + 2], parts[i + 3]
    base = re.split(r"[\\/]", name)[-1]
    rep = buf.get(base)
    if rep:
        content = replace_js(content, rep, base)
        nfiles += 1
    out.append(pre + num + ': "' + name + '" */' + content)
    i += 4
new_script = "".join(out)
if new_script.count("/* twine-user-script #") != script.count("/* twine-user-script #"):
    print("[AP01] FAIL 切分/拼回后头部数量不一致")
    sys.exit(1)
new_script = new_script + "\n" + MARK + "\n"
data = data[:cs] + new_script + data[ce:]

# ---- 校验：script 元素里不能出现 </script（会提前截断元素） ----
if "</script" in new_script.lower():
    print("[AP01] FAIL 译文里含 </script，会截断脚本元素")
    sys.exit(1)

# ---- 从包内 ModI18N 删除已烘焙的 JS 条目，防止运行时二次替换 ----
before = len(d["typeB"]["TypeBOutputText"])
d["typeB"]["TypeBOutputText"] = [
    v for v in d["typeB"]["TypeBOutputText"]
    if not (v.get("js") and (v.get("fileName"), v.get("pos"), v.get("f")) in baked)]
after = len(d["typeB"]["TypeBOutputText"])
new_i18n = json.dumps(d, ensure_ascii=False, indent=2).encode("utf-8")


def fn(name, b):
    return new_i18n if name == "i18n.json" else None


data, changed = MZ.patch_mod(data, "ModI18N", fn)
if changed != ["i18n.json"]:
    print("[AP01] FAIL 改写 ModI18N/i18n.json 失败: %s" % changed)
    sys.exit(1)
chk = json.loads(MZ.read_mod_file(data, "ModI18N", "i18n.json").decode("utf-8"))
if len(chk["typeB"]["TypeBOutputText"]) != after or len(chk["typeB"]["TypeBInputStoryScript"]) != len(d["typeB"]["TypeBInputStoryScript"]):
    print("[AP01] FAIL ModI18N/i18n.json 回读校验不一致")
    sys.exit(1)

open(HTML, "wb").write(data.encode("utf-8"))
print("[AP01] 官方 JS 译文：文件 %d / 条目 成功 %d 失败 %d   失败按文件 %s   ModI18N JS 条目 %d → %d" % (
    nfiles, stat["ok"], stat["fail"], sorted(fail_detail.items(), key=lambda x: -x[1])[:8], before, after))
sys.exit(0)
