// 验证 widget 宏是否通过 Macro 注册（而不是依赖 passage）
const fs = require("fs");
const path = require("path");
const http = require("http");
const { spawn } = require("child_process");
const os = require("os");

const INDEX = process.argv[2] || "E:\\TAML\\_dol\\work\\index_modded6.html";
const PORT_HTTP = 8895;
const PORT_CDP = 9525;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  const dir = path.dirname(INDEX);
  const server = http.createServer((req, res) => {
    const p = decodeURIComponent(req.url.split("?")[0]);
    const f = path.join(dir, p === "/" ? "index.html" : p.slice(1));
    fs.readFile(f, (e, d) => {
      if (e) { res.writeHead(404); res.end(); return; }
      const ext = path.extname(f).toLowerCase();
      const ct = ext === ".html" ? "text/html; charset=utf-8"
        : ext === ".png" ? "image/png" : ext === ".css" ? "text/css"
        : ext === ".js" ? "application/javascript" : "application/octet-stream";
      res.writeHead(200, { "Content-Type": ct });
      res.end(d);
    });
  });
  await new Promise((r) => server.listen(PORT_HTTP, "127.0.0.1", r));

  const PROFILE = path.join(os.tmpdir(), "cdp-macro-" + Date.now());
  fs.mkdirSync(PROFILE, { recursive: true });
  const proc = spawn("C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe", [
    "--headless=new", `--remote-debugging-port=${PORT_CDP}`, `--user-data-dir=${PROFILE}`,
    "--no-first-run", "--no-default-browser-check", "--disable-gpu",
    "--js-flags=--max-old-space-size=6144", "about:blank",
  ], { stdio: "ignore" });

  let targets = null;
  for (let i = 0; i < 225; i++) {
    await sleep(400);
    try {
      targets = await (await fetch(`http://127.0.0.1:${PORT_CDP}/json/list`)).json();
      if (targets && targets.length) break;
    } catch (e) { }
  }
  if (!targets || !targets.length) { console.log("❌ Edge 起不来"); process.exit(1); }
  const page = targets.find((t) => t.type === "page") || targets[0];
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0;
  const pend = new Map();
  const send = (m, p, to = 120000) => {
    const i = ++id;
    ws.send(JSON.stringify({ id: i, method: m, params: p || {} }));
    return new Promise((res) => { pend.set(i, res); setTimeout(() => { if (pend.has(i)) { pend.delete(i); res(null); } }, to); });
  };
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  ws.onmessage = (e) => {
    let m; try { m = JSON.parse(e.data); } catch (_) { return; }
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m.result); pend.delete(m.id); }
  };
  const evalJs = async (expr, to = 120000) => {
    const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true }, to);
    if (!r) return { __timeout: true };
    if (r.exceptionDetails) return { __exception: String(r.exceptionDetails.text).slice(0, 400) };
    return r.result ? r.result.value : null;
  };

  await send("Page.navigate", { url: `http://127.0.0.1:${PORT_HTTP}/index.html` });
  const t0 = Date.now();
  let ready = false;
  while ((Date.now() - t0) / 1000 < 200) {
    await sleep(3000);
    const v = await evalJs("typeof SugarCube!=='undefined' && !!SugarCube.State && !!SugarCube.State.passage", 20000);
    if (v === true) { ready = true; break; }
  }
  console.log("[就绪]", ready, Math.round((Date.now() - t0) / 1000) + "s");
  if (!ready) process.exit(1);
  await sleep(5000);

  const info = await evalJs(`(function(){
    var out = { macroCount: 0, probes: [], storyCount: 0, indexInDom: 0 };
    try {
      var M = SugarCube.Macro;
      if (M && M.get) {
        var map = {};
        // 用 Macro.get 逐个探测已知 widget 名
        var names = [
          'actionsanusPenisDoublePenetration', 'leftUndressOther', 'rightUndressOther',
          'lrtrauma', 'person', 'combatpersons', 'combatperson',
          'widget', 'actionsanus', 'updateChildActivity'
        ];
        for (var i = 0; i < names.length; i++) {
          var v = M.get(names[i]);
          out.probes.push({ name: names[i], exists: !!v, isWidget: !!(v && v.isWidget) });
        }
      }
    } catch (e) { out.err = e.message; }

    // Story 里 passage 总数
    try { out.storyCount = SugarCube.Story.lookup([]).length; } catch (e) {}

    // DOM 里的 tw-passagedata 总数（原始数据是否还在）
    try { out.indexInDom = document.querySelectorAll('tw-passagedata').length; } catch (e) {}

    // 找几个长 passage 是否在 Story
    var checks = ['Widgets Text', 'Widgets Combat Man-Combat', 'Widgets Effects Man', 'Widgets', 'Widgets variablesStatic'];
    out.longPsg = [];
    for (var j = 0; j < checks.length; j++) {
      try {
        var p = SugarCube.Story.get(checks[j]);
        out.longPsg.push({ name: checks[j], ok: !!(p && p.text && p.text.indexOf('error-view') < 0), len: p && p.text ? p.text.length : -1 });
      } catch (e) { out.longPsg.push({ name: checks[j], err: e.message }); }
    }
    return out;
  })()`, 120000);

  console.log("\\n=== Macro 注册情况 ===");
  if (info && info.probes) {
    for (const p of info.probes) {
      console.log("  %s %-36s %s", p.exists ? "OK  " : "缺失", p.name, p.isWidget ? "(widget)" : "");
    }
  }
  console.log("\\n=== Story 统计 ===");
  console.log("  Story passage 数     :", info && info.storyCount);
  console.log("  DOM tw-passagedata 数:", info && info.indexInDom);
  console.log("\\n=== 长 passage 检查 ===");
  if (info && info.longPsg) {
    for (const p of info.longPsg) {
      console.log("  %s %-32s len=%s", p.ok ? "OK  " : "⚠   ", p.name, p.len);
    }
  }

  try { ws.close(); } catch (e) { }
  try { server.close(); } catch (e) { }
  try { proc.kill(); } catch (e) { }
  try { fs.rmSync(PROFILE, { recursive: true, force: true }); } catch (e) { }
  process.exit(0);
})();
