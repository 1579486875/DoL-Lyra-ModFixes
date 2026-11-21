"""RT_GATE（第12轮建立）：运行时验证门 —— 在真实浏览器里加载整包，按 plan_gate.json 跑检查。

为什么需要：第12轮发现静态检查（REGRESS_ALL / validate / exec_verify 全绿）看不见的问题全在运行时：
  · ModI18N 运行时 JS 替换因位移失配 → 成就描述/提示大面积变英文
  · TweeReplacer 补丁（Quoted Link Fix）在运行时把 4 个 passage 的代码改坏
  · passage 正文裸 <</if>> 被浏览器 HTML 解析吞掉 → 运行时 '<>'
  · maplebirch 抢先改写导致 DoLSims/DomRobin 补丁失配
检查项：
  G1 页面能就绪
  G2 ModLoader 日志里没有 TweeReplacer / zone 补丁错误
  G3 运行时全部 passage+widget 的宏表达式经引擎 parse 后可编译（T03）
  G4 运行时宏结构不比 vanilla 多出错误（scan_lib.struct_regressions）
  G5 运行时成就 title/desc/hint 中文覆盖不低于黄金基线（298/299、299/299、152/152 的 -2 容差）
  G6 关键流程 / 组件渲染零红字
用法: python RT_GATE.py [apk 或 index.html]
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile

W = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, W)
import scan_lib as SL

src = sys.argv[1] if len(sys.argv) > 1 else (os.environ.get("DOL_APK") or r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk")
tmp = tempfile.mkdtemp(prefix="dsh_rtgate_")
idx = os.path.join(tmp, "index.html")
env = dict(os.environ)
www = None
if src.lower().endswith(".apk"):
    z = zipfile.ZipFile(src)
    open(idx, "wb").write(z.read("assets/www/index.html"))
    # 第13轮：同时解出静态资源交给 cdp_suite 提供，统计真实 404（缺图 / 缺脚本）
    www = os.path.join(tmp, "www")
    for n in z.namelist():
        if n.startswith("assets/www/") and not n.endswith("/") and n != "assets/www/index.html":
            p = os.path.join(www, *n[len("assets/www/"):].split("/"))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as f:
                f.write(z.read(n))
    env["DOL_WWW"] = www
else:
    idx = src
out_json = os.path.join(W, "_rt_gate.json")
r = subprocess.run(["node", os.path.join(W, "cdp_suite.js"), idx, os.path.join(W, "plan_gate.json"), out_json, "1500"],
                   cwd=W, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
print((r.stdout or "")[-3000:])
FAIL = []


def chk(name, ok, detail=""):
    print("  [%s] %s  %s" % ("OK  " if ok else "FAIL", name, detail))
    if not ok:
        FAIL.append(name)


if r.returncode != 0 or not os.path.exists(out_json):
    chk("G0 cdp_suite 运行", False, (r.stderr or "")[-500:])
    sys.exit(1)
rep = json.load(open(out_json, encoding="utf-8"))
chk("G1 页面就绪", rep.get("ready") is True, "%ss" % rep.get("readySec"))
steps = {s["name"]: s for s in rep["steps"]}
ml = steps.get("模组加载状态", {}).get("value") or {}
we = [x for x in (ml.get("logWarnErr") or []) if re.search(r"TweeReplacer|\[zone\]|passage patch did not apply", x)]
chk("G2 模组补丁零错误", not we, "%d 条 %s" % (len(we), [x[:160] for x in we[:4]]))

dump = os.path.join(W, "_rt_gate_passages.jsonl")
rt_html = os.path.join(tmp, "runtime_index.html")
subprocess.run([sys.executable, os.path.join(W, "AK01_runtime_to_html.py"), dump, rt_html], capture_output=True)
r3 = subprocess.run(["node", "--max-old-space-size=8192", os.path.join(W, "T03_sc_compile_all.js"), rt_html, os.path.join(tmp, "t03.json")],
                    capture_output=True, text=True, encoding="utf-8", errors="replace")
m3 = re.search(r"编译失败 (\d+)", r3.stdout or "")
n3 = int(m3.group(1)) if m3 else -1
det3 = ""
if n3 > 0:
    det3 = str([(e["passage"], e["macro"], e["err"][:60]) for e in json.load(open(os.path.join(tmp, "t03.json"), encoding="utf-8"))[:5]])
chk("G3 运行时宏表达式可编译", n3 == 0, "%d 处 %s" % (n3, det3))

van = open(os.path.join(W, "index.html"), "rb").read().decode("utf-8", "replace")
rtraw = open(rt_html, "rb").read().decode("utf-8", "replace")
sr = SL.struct_regressions(van, rtraw)
chk("G4 运行时宏结构不劣于 vanilla", not sr, "%d %s" % (len(sr), list(sr.items())[:3]))

ft = (steps.get("运行时文本(成就/服装描述)", {}).get("value") or {}).get("feats") or {}
t, dsc, hnt = ft.get("title", [0, 0]), ft.get("desc", [0, 0]), ft.get("hint", [0, 0])
chk("G5 成就中文覆盖", t[1] >= t[0] - 2 and dsc[1] >= dsc[0] - 2 and hnt[1] >= hnt[0] - 2,
    "title %s desc %s hint %s" % (t, dsc, hnt))

bad = []
warn = []
# 战斗收尾等「剧情中途」passage 直接跳转会缺状态（$enemyarousal / $NPCList 等），
# 这些步骤只把「语法 / 结构类」红字判失败，其它记为提示
LOOSE = {"Bully Toilets Fight Finish", "Fishing Moor Hiker Molestation Finish", "Livestock Escape Centaur",
         # 森林商店：$gwylanSeen 等在首次见到格威岚（npc 初始化）时才创建，新档直接跳转必然缺状态（vanilla 同样）
         "Forest Shop"}
HARD = re.compile(r"SyntaxError|cannot find a closing tag|child tag|does not exist|Unexpected token|is not defined|is not a function")
for s in rep["steps"]:
    if s["type"] in ("play", "wiki"):
        lst = (s.get("dom") or {}).get("list") or []
        n = (s.get("dom") or {}).get("n", 0)
        if n and n > 0:
            if s["name"] in LOOSE and not any(HARD.search(x) for x in lst):
                warn.append((s["name"], n, lst[0][:160] if lst else ""))
            else:
                bad.append((s["name"], n, (lst or [""])[0][:200]))
        if s["type"] == "play" and s.get("nav") not in ("OK",):
            bad.append((s["name"], "nav=" + str(s.get("nav")), ""))
chk("G6 关键流程零红字", not bad, str(bad[:6]))

# G7（第13轮）：查名函数走官方映射表（Npc Name CN 1.4.0）
cn = (steps.get("NPC_CN_TYPE 鱼名", {}).get("value") or {})
want = {"t_herring": "鲱鱼", "t_cod": "鳕鱼", "t_wolf": "狼", "t_eels": "鳗鱼"}
got = {k: cn.get(k) for k in want}
chk("G7 物种名中文（官方表优先）", got == want and not cn.get("fishUntranslated"),
    "%s 未翻鱼名=%s" % (got, cn.get("fishUntranslated")))

# G8（第13轮）：渲染出来的文字里不得残留宏括号（如社交面板「贝利>>」）
leak = []
for s in rep["steps"]:
    if s["type"] in ("play", "wiki"):
        txt = (s.get("dom") or {}).get("text") or ""
        for m in re.finditer(r"<<|>>", txt):
            leak.append((s["name"], txt[max(0, m.start() - 20):m.end() + 10]))
            break
chk("G8 渲染文本无宏括号残留", not leak, str(leak[:5]))

# G9（第13轮）：测试流程中请求到的静态资源没有 404（原版也没有的 3 个可选文件除外）
if www:
    OPTIONAL = {"modList.json", "style.css", "usettings.js"}
    miss = [(k, n) for k, n in (rep.get("http404") or []) if k not in OPTIONAL]
    chk("G9 静态资源无 404", not miss, "%d 种 %s" % (len(miss), miss[:8]))
try:
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
except Exception:
    pass
for w in warn:
    print("  [提示] 剧情中途跳转的状态缺失红字（非语法类，不判失败）:", w)
print("\nRT_GATE: %d 项失败" % len(FAIL) if FAIL else "\nRT_GATE: 全部通过")
sys.exit(1 if FAIL else 0)
