"""真实执行验证：把 <<script>> 抽出来，用 Node 模拟 setup，看函数是否真的挂上。"""
import html
import json
import os
import re
import subprocess
import tempfile
import zipfile

APK = r"E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk"
z = zipfile.ZipFile(APK)
g = html.unescape(z.read("assets/www/index.html").decode("utf-8", "replace"))

# 抽取我加的 4 个 <<script>>（含 typeof setup 的）
scripts = []
for m in re.finditer(r"<<script>>(.*?)<</script>>", g, re.S):
    src = m.group(1)
    if "typeof setup" in src:
        scripts.append(src)

print(f"找到 {len(scripts)} 个我加的 <<script>> 块")

TMP = os.path.join(tempfile.gettempdir(), "dsh_mock_test.js")
harness = """
// 模拟 SugarCube 环境
global.window = global;
var setup = {};
global.setup = setup;
var results = {};
try {
SETUP_SCRIPTS
} catch (e) {
    results.error = e.message;
}
// 检查挂了哪些函数
var want = ["description_CN","NPC_CN_TOOLNAME","NPC_CN_TYPE","NPC_CN_NAME",
            "NPC_CN_TITLE","BODYPARTS_CN_NAME","CAFE_FOOD_CN","DirectionCN",
            "brothelshowType_CN","update_cloth_cn"];
results.installed = {};
want.forEach(function(k){
    results.installed[k] = typeof setup[k];
});
results.calls = {};
try { results.calls.desc = setup.description_CN("tall"); } catch(e) { results.calls.descErr = e.message; }
try { results.calls.tool = setup.NPC_CN_TOOLNAME("dildo"); } catch(e) { results.calls.toolErr = e.message; }
try { results.calls.type = setup.NPC_CN_TYPE("lizard"); } catch(e) { results.calls.typeErr = e.message; }
try { results.calls.eels = setup.NPC_CN_TYPE("eels"); } catch(e) { results.calls.eelsErr = e.message; }
console.log(JSON.stringify(results, null, 2));
"""

body = "\n".join(scripts)
open(TMP, "w", encoding="utf-8").write(harness.replace("SETUP_SCRIPTS", body))

r = subprocess.run(["node", TMP], capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
print("\n=== Node 执行结果 ===")
print(r.stdout[-2500:] if r.stdout else "(无输出)")
if r.stderr:
    print("\n=== stderr ===")
    print(r.stderr[-2000:])
