"""AJ01：社区发布的 ModI18N（v0.5.12.13-chs-1.0.1a）与我们包内嵌的 ModI18N 逐文件对比（只读）。"""
import hashlib
import io
import json
import sys
import zipfile

sys.path.insert(0, r"E:\TAML\_dol\work")
import modzip_lib as M

up = zipfile.ZipFile(r"E:\TAML\_dol\upstream_cn\ModI18N-0.5.12.13-chs-1.0.1a.mod.zip")
data = open(r"E:\TAML\_dol\work\_cur_index.html", "rb").read().decode("utf-8", "replace")
ours = None
for s, zz, bj in M.iter_mods(data):
    if bj and bj.get("name") == "ModI18N":
        ours = zz
        break
h = lambda b: hashlib.sha256(b).hexdigest()[:16]
U = {i.filename: up.read(i.filename) for i in up.infolist() if not i.is_dir()}
O = {i.filename: ours.read(i.filename) for i in ours.infolist() if not i.is_dir()}
print("社区包文件 %d / 我们内嵌 %d" % (len(U), len(O)))
same = [f for f in U if f in O and U[f] == O[f]]
diff = [f for f in U if f in O and U[f] != O[f]]
only_u = [f for f in U if f not in O]
only_o = [f for f in O if f not in U]
print("完全相同 %d  内容不同 %d  仅社区有 %d  仅我们有 %d" % (len(same), len(diff), len(only_u), len(only_o)))
for f in diff:
    print("  ≠", f, len(U[f]), len(O[f]), h(U[f]), h(O[f]))
for f in only_u[:20]:
    print("  仅社区", f)
for f in only_o[:20]:
    print("  仅我们", f)
bu = json.loads(U["boot.json"].decode("utf-8-sig"))
bo = json.loads(O["boot.json"].decode("utf-8-sig"))
print("boot 版本 社区=%s 我们=%s" % (bu.get("version"), bo.get("version")))
