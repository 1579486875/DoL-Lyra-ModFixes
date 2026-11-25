// 手动 CDP 检查：打开 index，抓控制台错误和 SugarCube 状态
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");
const os = require("os");

const IDX = process.argv[2];
const PORT_HTTP = 8890 + Math.floor(Math.random() * 20);
const PORT_CDP = 9490 + Math.floor(Math.random() * 20);
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const http = require("http");
  const server = http.createServer((req, res) => {
    const u = decodeURIComponent(req.url.split("?")[0]);
    const f = path.join(path.dirname(IDX), u === "/" ? "index.html" : u);
    if (fs.existsSync(f) && fs.statSync(f).isFile()) {
      res.writeHead(200, { "Content-Type": f.endsWith(".html") ? "text/html; charset=utf-8" : "application/octet-stream" });
      fs.createReadStream(f).pipe(res);
    } else { res.writeHead(404); res.end("404"); }
  });
  await new Promise(r => server.listen(PORT_HTTP, "127.0.0.1", r));

  const PROFILE = path.join(os.tmpdir(), "cdp-manual-" + Date.now());
  fs.mkdirSync(PROFILE, { recursive: true });
  const proc = spawn("C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe", [
    "--headless=new", `--remote-debugging-port=${PORT_CDP}`, `--user-data-dir=${PROFILE}`,
    "--no-first-run", "--no-default-browser-check", "--disable-gpu",
    "--js-flags=--max-old-space-size=6144", "about:blank",
  ], { stdio: "ignore" });

  let targets = null;
  for (let i = 0; i < 60; i++) {
    await sleep(400);
    try { targets = await (await fetch(`http://127.0.0.1:${PORT_CDP}/json/list`)).json(); if (targets && targets.length) break; } catch (e) {}
  }
  if (!targets) { console.log("CDP 未启动"); proc.kill(); server.close(); return; }
  const page = targets.find(t => t.type === "page") || targets[0];
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0; const pend = new Map();
  const send = (m, p) => new Promise((res, rej) => { const i = ++id; pend.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method: m, params: p || {} })); setTimeout(() => { if (pend.has(i)) { pend.delete(i); rej(new Error("timeout " + m)); } }, 120000); });
  const logs = [];
  ws.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pend.has(m.id)) { const p = pend.get(m.id); pend.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); }
    else if (m.method === "Runtime.consoleAPICalled") {
      logs.push("[" + m.params.type + "] " + (m.params.args || []).map(a => a.value !== undefined ? String(a.value) : (a.description || "")).join(" ").slice(0, 300));
    } else if (m.method === "Runtime.exceptionThrown") {
      logs.push("[EXCEPTION] " + (m.params.exceptionDetails?.exception?.description || m.params.exceptionDetails?.text || "").slice(0, 400));
    }
  };
  await new Promise(r => ws.onopen = r);
  await send("Runtime.enable");
  await send("Page.enable");
  const evalJs = async (expr, to = 30000) => {
    const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: false });
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.text + " " + (r.exceptionDetails.exception?.description || ""));
    return r.result.value;
  };

  console.log("导航到 index ...");
  await send("Page.navigate", { url: `http://127.0.0.1:${PORT_HTTP}/index.html` });

  const t0 = Date.now();
  let ready = false, lastState = "";
  for (let i = 0; i < 100; i++) {
    await sleep(3000);
    try {
      const st = await evalJs(`JSON.stringify({
        sc: typeof SugarCube,
        story: typeof (window.SugarCube && SugarCube.Story),
        state: typeof (window.SugarCube && SugarCube.State),
        passage: (window.SugarCube && SugarCube.State && SugarCube.State.passage) || null,
        hasSC: !!window.SugarCube,
        jQuery: typeof jQuery,
        bodyChildren: document.body ? document.body.children.length : -1,
        passageEls: document.querySelectorAll('#passages .passage').length,
        errs: document.querySelectorAll('.error, .error-view, .macro-error').length
      })`, 20000);
      lastState = st;
      const o = JSON.parse(st);
      if (o.passage) { ready = true; break; }
      if (i % 5 === 0) console.log(`  ${Math.round((Date.now() - t0) / 1000)}s  ${st}`);
    } catch (e) {
      console.log(`  ${Math.round((Date.now() - t0) / 1000)}s  eval 失败: ${String(e.message).slice(0, 120)}`);
    }
  }
  console.log(`\n[就绪] ${ready}  ${Math.round((Date.now() - t0) / 1000)}s`);
  console.log("[最终状态]", lastState);
  console.log(`\n[控制台日志] ${logs.length} 条`);
  for (const l of logs.slice(0, 40)) console.log("  " + l);

  try { ws.close(); } catch (e) {}
  proc.kill();
  server.close();
  fs.rmSync(PROFILE, { recursive: true, force: true });
  process.exit(0);
})().catch(e => { console.error("FATAL", e); process.exit(1); });
