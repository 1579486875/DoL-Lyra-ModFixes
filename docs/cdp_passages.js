/**
 * 多 passage 遍历测试：用 Engine.play() 逐个跳转，收集每个 passage 的错误。
 */
const { spawn } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");
const http = require("http");

const APK = process.argv[2];
const WORK = path.join(os.tmpdir(), "dsh-multi-" + Date.now());
const PORT_HTTP = 8821;
const PORT_CDP = 9411;

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

const PASSAGES = [
  "Start", "Options", "Cheats", "Wardrobe", "Characteristics",
  "Settings", "Journal", "Social", "Bodywriting", "Transformations",
  "Museum", "Shop", "Forest", "Beach", "School", "Hospital",
  "Orphanage Intro", "Bailey's Office", "Tutorial",
];

(async () => {
  fs.mkdirSync(WORK, { recursive: true });
  console.log("[1/5] 提取 APK ...");
  const { execSync } = require("child_process");
  execSync(`python -c "import zipfile;z=zipfile.ZipFile(r'${APK}');open(r'${path.join(WORK, 'index.html')}','wb').write(z.read('assets/www/index.html'))"`, { stdio: "inherit" });

  // 也提取 img（避免 404 噪音）
  console.log("[2/5] 提取 img（仅供加载，可能较慢）...");
  try {
    execSync(`python -c "import zipfile,os;p=r'${WORK}';z=zipfile.ZipFile(r'${APK}');ns=[n for n in z.namelist() if n.startswith('assets/www/img/face/masks')];[ (os.makedirs(os.path.dirname(os.path.join(p,n.replace('assets/www/',''))),exist_ok=True), open(os.path.join(p,n.replace('assets/www/','')),'wb').write(z.read(n))) for n in ns]"`, { stdio: "ignore" });
    console.log("    完成");
  } catch (e) { console.log("    (跳过)"); }

  const server = http.createServer((req, res) => {
    const p = path.join(WORK, decodeURIComponent(req.url.split("?")[0]));
    if (!fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); res.end(""); return; }
    const ext = path.extname(p);
    const ct = ext === ".html" ? "text/html; charset=utf-8"
      : ext === ".png" ? "image/png" : "application/octet-stream";
    res.writeHead(200, { "Content-Type": ct });
    fs.createReadStream(p).pipe(res);
  });
  await new Promise(r => server.listen(PORT_HTTP, "127.0.0.1", r));

  console.log("[3/5] 启动 Edge ...");
  const PROFILE = path.join(os.tmpdir(), "dsh-edge3-" + Date.now());
  fs.mkdirSync(PROFILE, { recursive: true });
  const proc = spawn("C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe", [
    "--headless=new", `--remote-debugging-port=${PORT_CDP}`,
    `--user-data-dir=${PROFILE}`, "--no-first-run", "--no-default-browser-check",
    "--disable-gpu", "--js-flags=--max-old-space-size=4096", "about:blank",
  ], { stdio: ["ignore", "pipe", "pipe"] });

  let targets = null;
  for (let i = 0; i < 80; i++) {
    await sleep(400);
    try {
      const r = await fetch(`http://127.0.0.1:${PORT_CDP}/json/list`);
      targets = await r.json();
      if (targets && targets.length) break;
    } catch (e) { }
  }
  const page = targets.find(t => t.type === "page") || targets[0];
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0;
  const pend = new Map();
  const send = (m, p) => {
    const i = ++id;
    ws.send(JSON.stringify({ id: i, method: m, params: p || {} }));
    return new Promise(res => { pend.set(i, res); setTimeout(() => { if (pend.has(i)) { pend.delete(i); res(null); } }, 40000); });
  };
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });

  let bucket = [];
  ws.onmessage = e => {
    let m; try { m = JSON.parse(e.data); } catch (_) { return; }
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m.result); pend.delete(m.id); return; }
    if (m.method === "Runtime.exceptionThrown") {
      const d = m.params.exceptionDetails;
      const t = d.exception && (d.exception.description || d.exception.value) || d.text;
      bucket.push({ k: "exception", t: String(t).split("\n")[0].slice(0, 260) });
    } else if (m.method === "Runtime.consoleAPICalled" && m.params.type === "error") {
      const a = (m.params.args || []).map(x => x.value !== undefined ? String(x.value) : (x.description || x.type)).join(" ");
      bucket.push({ k: "console.error", t: a.split("\n")[0].slice(0, 260) });
    }
  };

  await send("Runtime.enable");
  await send("Page.enable");
  await send("Page.navigate", { url: `http://127.0.0.1:${PORT_HTTP}/index.html` });

  console.log("[4/5] 等待启动 ...");
  const t0 = Date.now();
  while ((Date.now() - t0) / 1000 < 240) {
    await sleep(2000);
    const r = await send("Runtime.evaluate", {
      expression: "typeof setup!=='undefined'&&typeof State!=='undefined'&&!!State.passage",
      returnByValue: true,
    });
    if (r && r.result && r.result.value === true) break;
  }
  console.log(`    就绪 ${Math.round((Date.now() - t0) / 1000)}s，等模组加载 ...`);
  await sleep(12000);

  console.log("[5/5] 遍历 passage ...\n");
  const results = [];
  for (const p of PASSAGES) {
    bucket = [];
    const r = await send("Runtime.evaluate", {
      expression: `(function(){
      try {
        var E = window.Engine || (window.SugarCube && window.SugarCube.Engine);
        if (E && typeof E.play === "function") { E.play(${JSON.stringify(p)}); return "OK"; }
        var D = (window.SugarCube && window.SugarCube.State && window.SugarCube.State.display);
        if (typeof D === "function") { D(${JSON.stringify(p)}); return "OK_display"; }
        var W = window.SugarCube && window.SugarCube.Wikifier;
        if (W && typeof W.wikifyEval === "function") { W.wikifyEval("<<goto " + JSON.stringify(${JSON.stringify(p)}) + ">>"); return "OK_goto"; }
        return "NO_API:Engine=" + (typeof window.Engine) + ",SC=" + (typeof window.SugarCube) + ",SCE=" + (window.SugarCube && typeof window.SugarCube.Engine);
      } catch (e) { return "ERR:" + e.message; }
    })()`,
      returnByValue: true,
    });
    const nav = r && r.result && r.result.value;
    await sleep(2500);

    // 过滤噪音
    const real = bucket.filter(x =>
      !/tryReplaceStringFuzzyWithHint/.test(x.t) &&
      !/ModOrderContainer|ModI18NTypeB|cannot find name\/alias/.test(x.t) &&
      !/Failed to load resource|404|DOCTYPE|is not valid JSON/.test(x.t) &&
      !/Failed to load mask|Failed to load img/.test(x.t) &&
      !/drawImage/.test(x.t) &&
      !/randomInt called with invalid/.test(x.t)
    );
    results.push({ passage: p, nav, total: bucket.length, real });

    const mark = real.length === 0 ? "✅" : "❌";
    console.log(`  ${mark} ${p.padEnd(24)} 导航=${nav}  总错误=${bucket.length}  真问题=${real.length}`);
    if (real.length) {
      for (const x of real.slice(0, 3)) console.log(`       [${x.k}] ${x.t}`);
    }
  }

  console.log("\n" + "=".repeat(80));
  const withProblems = results.filter(r => r.real.length > 0);
  console.log(`遍历 ${results.length} 个 passage，有真问题的 ${withProblems.length} 个`);
  console.log("=".repeat(80));

  try { ws.close(); } catch (e) { }
  try { proc.kill(); } catch (e) { }
  server.close();
  await sleep(600);
  try { fs.rmSync(PROFILE, { recursive: true, force: true }); } catch (e) { }
  try { fs.rmSync(WORK, { recursive: true, force: true }); } catch (e) { }
  process.exit(withProblems.length ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
