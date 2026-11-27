// 深查：这些 passage 在运行时 Story 里的真实内容和长度
const fs = require("fs");
const path = require("path");
const http = require("http");
const { spawn } = require("child_process");
const os = require("os");

const INDEX = process.argv[2] || "E:\\TAML\\_dol\\work\\index_modded6.html";
const PORT_HTTP = 8894;
const PORT_CDP = 9524;
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

  const PROFILE = path.join(os.tmpdir(), "cdp-deep-" + Date.now());
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

  const NAME = "Widgets Actions Generation";
  const info = await evalJs(`(function(){
    var Story = SugarCube.Story;
    var out = { hasGet: typeof Story.get, hasLookup: typeof Story.lookup };
    var p = Story.get(${JSON.stringify(NAME)});
    out.found = !!p;
    if (p) {
      out.keys = Object.keys(p);
      out.name = p.name;
      out.textLen = (p.text||'').length;
      out.textHead = String(p.text||'').slice(0, 300);
      out.hasDom = !!p.domId;
      // 试 domId 对应的元素
      try {
        var el = document.getElementById(p.domId);
        out.domLen = el ? (el.textContent||'').length : -1;
        out.domHead = el ? String(el.textContent||'').slice(0, 300) : '';
      } catch(e) { out.domErr = e.message; }
    }
    // 列出所有名字含 "Actions Generation" 的
    out.matches = [];
    try {
      Story.lookup([]).forEach(function(x){
        if (x.name && x.name.indexOf('Actions Generation') >= 0) {
          out.matches.push({ name: x.name, len: (x.text||'').length });
        }
      });
    } catch(e) {}
    return out;
  })()`, 120000);

  console.log("\\n=== Story.get('" + NAME + "') ===");
  console.log(JSON.stringify(info, null, 1).slice(0, 2500));

  try { ws.close(); } catch (e) { }
  try { server.close(); } catch (e) { }
  try { proc.kill(); } catch (e) { }
  try { fs.rmSync(PROFILE, { recursive: true, force: true }); } catch (e) { }
  process.exit(0);
})();
