"""AK09（第12轮）：恢复 passage 源码里被「多解了一层」的 HTML 实体（幂等）。

现象（第12轮运行时验证门实测）：服装店分页按钮源码是
    <div class="btn-pagination-arrow">&lt;</div>
构建链里某处把它多反转义了一次，变成 <div class="btn-pagination-arrow"><</div>，
SugarCube 把 `<</div> … <<for …>>` 当成一个名叫 /div 的宏 → 「macro <</div>> does not exist」+
「child tag <</for>> was found outside」，服装店（以及场景回看、孩子列表）分页整段报错。
同批还有：Bedroom / Widgets Furniture 的 startsWith('&lt;&lt;')（自定义家具名的转义检查）被改成 '<<'（判断失效），
&nbsp; / &#x25B2; / &#8194; 变成字面字符（显示相同，但与原版不一致）。

修法（对照 vanilla 源码，不猜）：
  只处理标记类实体（&lt; &gt; &amp; 及其组合，如 '&lt;&lt'）：取 vanilla 里该实体的左右上下文（HTML/代码，不会被翻译），
  在当前源码里找「左上下文 + 中间段 + 右上下文」且中间段解码后与 vanilla 相同、写法不同的位置，按出现顺序一一换回；
  数量对不上就报告、不改（exit 1）。
  &nbsp; / &#x25B2; / &#8194; 的变化来自官方译文本身（译者删掉或直接写字符，AK10 已核实 12 条），不属于 bug，不处理。
根因：X05_fix_leaks.py 为修「双重转义」做了全文件 raw.replace("&amp;lt;", "&lt;")，
      把 vanilla 源码里合法的 &lt; 实体也一起解掉了（REGRESS 的 C.no_double_escape 断言要求 &amp;lt; 为 0，同样是错的）。
"""
import html as H
import os
import re
import sys

HTML = os.environ.get("DOL_HTML") or r"E:\TAML\_dol\work\index_modded6.html"
VAN = r"E:\TAML\_dol\work\index.html"
PAT = re.compile(r'(<tw-passagedata\s+[^>]*name="([^"]*)"[^>]*>)(.*?)(</tw-passagedata>)', re.S)
ENT = re.compile(r"(?:&(?:lt|gt|amp);?)+")

data = open(HTML, "rb").read().decode("utf-8", "replace")
if len(re.findall(r'<tw-passagedata[^>]*name="', data)) < 16000:
    print("[AK09] index 形态异常")
    sys.exit(1)

V = {}
for m in PAT.finditer(open(VAN, "rb").read().decode("utf-8", "replace")):
    src = H.unescape(m.group(3))
    if ENT.search(src):
        V[m.group(2)] = src

stat = {"passage": 0, "markup": 0}
unresolved = []


def restore(name, vs, cur):
    groups = {}
    for e in ENT.finditer(vs):
        run = e.group(0)
        dec = H.unescape(run)
        L = H.unescape(vs[max(0, e.start() - 16):e.start()])
        R = H.unescape(vs[e.end():e.end() + 16])
        groups.setdefault((L, R), []).append((run, dec))
    edits = []
    for (L, R), items in groups.items():
        maxlen = max(len(r) for r, _ in items)
        cands = []
        for m in re.finditer(re.escape(L) + r"(.{1,%d}?)" % maxlen + re.escape(R), cur, re.S):
            cands.append((m.start(1), m.group(1)))
        if len(cands) != len(items):
            unresolved.append((name, items[0][0], L[-16:] + "‹…›" + R[:16], "当前 %d 处 / vanilla %d 处" % (len(cands), len(items))))
            continue
        for (p, mid), (run, dec) in zip(cands, items):
            if mid == run:
                continue
            if H.unescape(mid) != dec:
                unresolved.append((name, run, L[-16:] + "‹" + mid + "›" + R[:16], "中间段解码不一致"))
                continue
            edits.append((p, len(mid), run))
    for p, ln, run in sorted(edits, reverse=True):
        cur = cur[:p] + run + cur[p + ln:]
        stat["markup"] += 1
    return cur


def fix(m):
    name = m.group(2)
    vs = V.get(name)
    if vs is None:
        return m.group(0)
    cur = H.unescape(m.group(3))
    new = restore(name, vs, cur)
    if new == cur:
        return m.group(0)
    stat["passage"] += 1
    return m.group(1) + H.escape(new, quote=False) + m.group(4)


new = PAT.sub(fix, data)
if stat["passage"]:
    open(HTML, "wb").write(new.encode("utf-8"))
print("[AK09] 恢复实体：passage %d / 标记类 %d 处；无法定位 %d 处" % (
    stat["passage"], stat["markup"], len(unresolved)))
for x in unresolved[:20]:
    print("    ", x)
sys.exit(1 if unresolved else 0)
