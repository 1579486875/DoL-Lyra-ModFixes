/**
 * cdp_suite.js（第12轮）：一次加载游戏，按计划跑多个运行时检查，并且**统计页面里的 SugarCube 红字**。
 *
 * 旧的 cdp_flow.js 只收集 Runtime.exceptionThrown 和 console.error —— 但 SugarCube 的宏错误
 * （<<set>>: bad evaluation …）是渲染进页面的 <span class="error">，不会抛异常，
 * 所以旧流程「10 步 0 错误」看不见这类红字。本工具每一步都数 DOM 里的 .error。
 *
 * 用法: node cdp_suite.js <index.html 路径> <plan.json> <out.json> [就绪超时秒=900]
 * plan.json: [{"type":"play","name":"Clothing Shop"}, {"type":"wiki","name":"社交面板","code":"<<social>>"},
 *             {"type":"eval","name":"xx","file":"probe_x.js"}]
 */
const { spawn } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");
const http = require("http");

const INDEX = path.resolve(process.argv[2]);
const PLAN = JSON.parse(fs.readFileSync(process.argv[3], "utf8"));
const OUT = process.argv[4];
const READY_TIMEOUT = parseInt(process.argv[5] || "900", 10);
const PORT_HTTP = 8860 + Math.floor(Math.random() * 30);
const PORT_CDP = 9460 + Math.floor(Math.random() * 30);
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  // 第13轮：DOL_WWW=<解出的 assets/www 目录> 时同时提供静态资源，并记录 404（真实缺图，§3.12 L 类运行时版）
  const WWW = process.env.DOL_WWW ? path.resolve(process.env.DOL_WWW) : null;
  const MIME = { ".png": "image/png", ".gif": "image/gif", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp",
    ".svg": "image/svg+xml", ".css": "text/css", ".js": "text/javascript", ".json": "application/json", ".woff2": "font/woff2",
    ".woff": "font/woff", ".ttf": "font/ttf", ".mp3": "audio/mpeg", ".ogg": "audio/ogg" };
  const http404 = {};
  const server = http.createServer((req, res) => {
    const u = decodeURIComponent(req.url.split("?")[0]);
    if (u === "/" || u === "/index.html") {
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      fs.createReadStream(INDEX).pipe(res);
      return;
    }
    if (WWW) {
      const p = path.join(WWW, u.replace(/^\/+/, ""));
      if (p.startsWith(WWW) && fs.existsSync(p) && fs.statSync(p).isFile()) {
        res.writeHead(200, { "Content-Type": MIME[path.extname(p).toLowerCase()] || "application/octet-stream" });
        fs.createReadStream(p).pipe(res);
        return;
      }
      const k = u.replace(/^\/+/, "");
      http404[k] = (http404[k] || 0) + 1;
    }
    res.writeHead(404); res.end("");
  });
  await new Promise(r => server.listen(PORT_HTTP, "127.0.0.1", r));

  const PROFILE = path.join(os.tmpdir(), "dsh-suite-" + Date.now());
  fs.mkdirSync(PROFILE, { recursive: true });
  const proc = spawn("C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe", [
    "--headless=new", `--remote-debugging-port=${PORT_CDP}`, `--user-data-dir=${PROFILE}`,
    "--no-first-run", "--no-default-browser-check", "--disable-gpu",
    "--js-flags=--max-old-space-size=6144", "about:blank",
  ], { stdio: ["ignore", "pipe", "pipe"] });

  let targets = null;
  for (let i = 0; i < 100; i++) {
    await sleep(400);
    try { targets = await (await fetch(`http://127.0.0.1:${PORT_CDP}/json/list`)).json(); if (targets && targets.length) break; } catch (e) { }
  }
  const page = targets.find(t => t.type === "page") || targets[0];
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0;
  const pend = new Map();
  const send = (m, p, to = 120000) => {
    const i = ++id;
    ws.send(JSON.stringify({ id: i, method: m, params: p || {} }));
    return new Promise(res => { pend.set(i, res); setTimeout(() => { if (pend.has(i)) { pend.delete(i); res(null); } }, to); });
  };
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  let bucket = [];
  const dialogs = [];
  ws.onmessage = e => {
    let m; try { m = JSON.parse(e.data); } catch (_) { return; }
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m.result); pend.delete(m.id); return; }
    if (m.method === "Page.javascriptDialogOpening") {
      // alert()/confirm() 会阻塞页面：记录并自动关闭（SugarCube 启动期脚本出错走的就是 Alert）
      dialogs.push(String(m.params.type) + ": " + String(m.params.message).slice(0, 1500));
      const i = ++id;
      ws.send(JSON.stringify({ id: i, method: "Page.handleJavaScriptDialog", params: { accept: true } }));
      return;
    }
    if (m.method === "Runtime.exceptionThrown") {
      const d = m.params.exceptionDetails;
      bucket.push("[exception] " + String((d.exception && (d.exception.description || d.exception.value)) || d.text).split("\n")[0].slice(0, 300));
    } else if (m.method === "Runtime.consoleAPICalled" && (m.params.type === "error" || m.params.type === "warning")) {
      const args = m.params.args || [];
      const a = args.map(x => x.value !== undefined ? String(x.value) : (x.description || x.type)).join(" ");
      bucket.push("[console." + m.params.type + "] " + a.split("\n")[0].slice(0, 300));
      if (/tryReplaceStringFuzzyWithHint/.test(a)) {
        // ModI18N 运行时替换失败：把「要找的原文」预览取出来（args[1] 是数组，preview 里有前 100 字）
        const pv = args.map(x => x.preview && x.preview.properties ? x.preview.properties.map(p => p.value).join(" | ") : "").filter(Boolean);
        (globalThis.__fuzzy = globalThis.__fuzzy || []).push(pv.join(" ### ").slice(0, 400));
      }
    }
  };
  await send("Runtime.enable");
  await send("Page.enable");
  const evalJs = async (expr, to) => {
    const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true }, to);
    if (!r) return { __timeout: true };
    if (r.exceptionDetails) return { __exception: String(r.exceptionDetails.exception && r.exceptionDetails.exception.description || r.exceptionDetails.text).slice(0, 400) };
    return r.result ? r.result.value : null;
  };

  const report = { index: INDEX, steps: [] };
  const t0 = Date.now();
  await send("Page.navigate", { url: `http://127.0.0.1:${PORT_HTTP}/index.html` });
  let ready = false;
  while ((Date.now() - t0) / 1000 < READY_TIMEOUT) {
    await sleep(3000);
    const v = await evalJs("typeof SugarCube!=='undefined' && !!SugarCube.State && !!SugarCube.State.passage", 20000);
    if (v === true) { ready = true; break; }
  }
  report.readySec = Math.round((Date.now() - t0) / 1000);
  report.ready = ready;
  report.loadNoise = bucket.slice(0, 400);
  const agg = {};
  for (const x of bucket) { const k = x.replace(/\d+/g, "#").slice(0, 120); agg[k] = (agg[k] || 0) + 1; }
  report.loadNoiseAgg = Object.entries(agg).sort((a, b) => b[1] - a[1]).slice(0, 60);
  report.loadNoiseTotal = bucket.length;
  report.fuzzyFails = globalThis.__fuzzy || [];
  report.dialogs = dialogs;
  if (dialogs.length) console.log("[弹窗] " + dialogs.length + " 个：\n  " + dialogs.map(x => x.slice(0, 400)).join("\n  "));
  console.log(`[就绪] ${ready} ${report.readySec}s  加载期日志 ${bucket.length} 条`);
  await sleep(8000);

  const DOM_ERR = `(function(sel){var r=document.querySelector(sel);if(!r)return {n:-1,list:[]};
    var l=Array.from(r.querySelectorAll('.error, .error-view, .macro-error'));
    return {n:l.length, list:l.slice(0,12).map(function(x){return (x.getAttribute('title')||'').slice(0,240)+' ⟹ '+x.textContent.slice(0,240);})};})`;

  for (const st of PLAN) {
    bucket = [];
    const rec = { type: st.type, name: st.name };
    if (st.type === "play") {
      rec.nav = await evalJs(`(function(){try{var SC=window.SugarCube;if(!SC.Story.has(${JSON.stringify(st.name)}))return "NO_PASSAGE";
        ${st.pre || ""}
        SC.Engine.play(${JSON.stringify(st.name)});return "OK";}catch(e){return "ERR:"+e.message;}})()`);
      await sleep(st.wait || 3000);
      rec.passage = await evalJs("SugarCube.State.passage");
      rec.dom = await evalJs(DOM_ERR + "('#passages')");
    } else if (st.type === "wiki") {
      rec.dom = await evalJs(`(function(){try{${st.pre || ""}
        var d=document.createElement('div');d.id='__suite_wiki';document.body.appendChild(d);
        new SugarCube.Wikifier(d, ${JSON.stringify(st.code)});
        var r=${DOM_ERR}('#__suite_wiki');r.text=d.textContent.replace(/\\s+/g,' ').slice(0,${st.textLen || 300});d.remove();return r;}
        catch(e){return {n:-2,err:String(e).slice(0,300)};}})()`);
      await sleep(500);
    } else if (st.type === "eval") {
      const src = fs.readFileSync(path.resolve(path.dirname(process.argv[3]), st.file), "utf8");
      const v = await evalJs(src, 300000);
      try { rec.value = typeof v === "string" ? JSON.parse(v) : v; } catch (e) { rec.value = v; }
    } else if (st.type === "dump") {
      // 把运行时（ModI18N / TweeReplacer / 各模组改写之后）的全部 passage 原文导出，供静态工具复查
      const n = await evalJs("(window.__dumpList = [].concat(" +
        "SugarCube.Story.lookupWith(function(){return true;}).map(function(p){return [p.title, (p.tags||[]).join(' '), p.text];})," +
        "SugarCube.Story.getAllWidget().map(function(p){return [p.title, (p.tags||[]).join(' '), p.text];})," +
        "SugarCube.Story.getAllInit().map(function(p){return [p.title, (p.tags||[]).join(' '), p.text];})," +
        "SugarCube.Story.getAllScript().map(function(p){return [p.title, 'script ' + (p.tags||[]).join(' '), p.text];})" +
        ")).length", 300000);
      rec.total = n;
      const outPath = path.resolve(path.dirname(process.argv[3]), st.out || "_runtime_passages.jsonl");
      const fd = fs.openSync(outPath, "w");
      const CH = 800;
      for (let i = 0; typeof n === "number" && i < n; i += CH) {
        const part = await evalJs(`JSON.stringify(window.__dumpList.slice(${i}, ${i + CH}))`, 300000);
        if (typeof part !== "string") { rec.err = "chunk " + i + " 失败"; break; }
        for (const row of JSON.parse(part)) fs.writeSync(fd, JSON.stringify(row) + "\n");
      }
      fs.closeSync(fd);
      rec.out = outPath;
    }
    rec.log = bucket.filter(x => !/Failed to load resource|net::ERR|404/.test(x)).slice(0, 30);
    report.steps.push(rec);
    const n = rec.dom ? rec.dom.n : "-";
    console.log(`  [${st.type}] ${String(st.name).padEnd(34)} 红字=${n}  日志=${rec.log.length}${rec.nav ? "  nav=" + rec.nav : ""}${rec.passage ? " → " + rec.passage : ""}`);
    if (rec.dom && rec.dom.list) for (const x of rec.dom.list.slice(0, 3)) console.log("        " + x.slice(0, 260));
  }

  if (WWW) {
    report.http404 = Object.entries(http404).sort((a, b) => b[1] - a[1]);
    console.log(`[静态资源] 404 共 ${report.http404.length} 种`);
  }
  fs.writeFileSync(OUT, JSON.stringify(report, null, 1), "utf8");
  try { ws.close(); } catch (e) { }
  try { proc.kill(); } catch (e) { }
  server.close();
  await sleep(800);
  try { fs.rmSync(PROFILE, { recursive: true, force: true }); } catch (e) { }
  process.exit(0);
})().catch(e => { console.error(e); process.exit(2); });
