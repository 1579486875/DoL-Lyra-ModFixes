/**
 * 存档往返测试：跳到可存档 passage -> 序列化 -> 反序列化 -> 比对。
 * 一次 CDP 连接内完成，避免多次 80s 加载。
 */
const { spawn, execSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");
const http = require("http");

const APK = process.argv[2];
const WORK = path.join(os.tmpdir(), "dsh-save-" + Date.now());
const PORT_HTTP = 8841;
const PORT_CDP = 9441;

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

(async () => {
  fs.mkdirSync(WORK, { recursive: true });
  console.log("[1/5] 提取 APK ...");
  execSync(`python -c "import zipfile,os;p=r'${WORK}';z=zipfile.ZipFile(r'${APK}');` +
    `open(os.path.join(p,'index.html'),'wb').write(z.read('assets/www/index.html'));` +
    `ns=[n for n in z.namelist() if n.startswith('assets/www/img/face/masks')];` +
    `[ (os.makedirs(os.path.dirname(os.path.join(p,n.replace('assets/www/',''))),exist_ok=True), open(os.path.join(p,n.replace('assets/www/','')),'wb').write(z.read(n))) for n in ns ]"`,
    { stdio: "inherit" });

  const server = http.createServer((req, res) => {
    const p = path.join(WORK, decodeURIComponent(req.url.split("?")[0]));
    if (!fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); res.end(""); return; }
    res.writeHead(200, { "Content-Type": p.endsWith(".html") ? "text/html; charset=utf-8" : "image/png" });
    fs.createReadStream(p).pipe(res);
  });
  await new Promise(r => server.listen(PORT_HTTP, "127.0.0.1", r));

  console.log("[2/5] 启动 Edge ...");
  const PROFILE = path.join(os.tmpdir(), "dsh-sv-" + Date.now());
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
    return new Promise(res => { pend.set(i, res); setTimeout(() => { if (pend.has(i)) { pend.delete(i); res(null); } }, 60000); });
  };
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  ws.onmessage = e => {
    let m; try { m = JSON.parse(e.data); } catch (_) { return; }
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m.result); pend.delete(m.id); }
  };
  await send("Runtime.enable");
  await send("Page.navigate", { url: `http://127.0.0.1:${PORT_HTTP}/index.html` });

  console.log("[3/5] 等待就绪 ...");
  const t0 = Date.now();
  while ((Date.now() - t0) / 1000 < 250) {
    await sleep(2000);
    const r = await send("Runtime.evaluate", {
      expression: "typeof setup!=='undefined'&&typeof State!=='undefined'&&!!State.passage",
      returnByValue: true,
    });
    if (r && r.result && r.result.value === true) break;
  }
  console.log(`    ${Math.round((Date.now() - t0) / 1000)}s`);
  await sleep(10000);

  const evalJs = async (expr) => {
    const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true });
    return r && r.result ? (r.result.value !== undefined ? r.result.value : r.result.description) : null;
  };

  console.log("[4/5] 探测 Save API ...");
  const api = await evalJs(`JSON.stringify((function(){
    var SC = window.SugarCube;
    if (!SC) return {err:"no SC"};
    var S = SC.Save;
    return {
      hasSave: typeof S,
      methods: S ? Object.keys(S).slice(0, 20) : [],
      serialize: S ? typeof S.serialize : "no",
      deserialize: S ? typeof S.deserialize : "no",
      saveToStorage: S ? typeof S.saveToStorage : "no",
      passage: SC.State.passage
    };
  })())`);
  console.log("   ", api);

  console.log("[5/5] 跳到可存档 passage ...");
  // 先跳到一个普通 passage
  const nav = await evalJs(`(function(){
    try {
      var SC = window.SugarCube;
      SC.Engine.play("Bedroom");
      return "QUEUED";
    } catch(e){ return "ERR:" + e.message; }
  })()`);
  console.log("   nav:", nav);
  await sleep(4000);
  const p2 = await evalJs("window.SugarCube.State.passage");
  console.log("   现在 passage:", p2);

  // 序列化
  console.log("\n=== 序列化测试 ===");
  const ser = await evalJs(`JSON.stringify((function(){
    try {
      var SC = window.SugarCube;
      var V = SC.State.variables;
      var keys = ["player","worn","NPCList","settings","location","hairlength","money"];
      var before = {};
      keys.forEach(function(k){
        try { before[k] = (V[k]===undefined) ? "UNDEF" : (typeof V[k]==="object" ? JSON.stringify(V[k]).length : String(V[k])); }
        catch(e){ before[k]="ERR"; }
      });
      var data = null, err = null;
      try { data = SC.Save.serialize(); } catch(e){ err = String(e.message||e).slice(0,200); }
      var out = { before: before, serLen: data ? data.length : 0, serErr: err, passage: SC.State.passage };

      if (data && data.length > 0) {
        var obj = null, derr = null;
        try { obj = SC.Save.deserialize(data); } catch(e){ derr = String(e.message||e).slice(0,200); }
        out.deOk = !!obj;
        out.deErr = derr;
        // deserialize 可能无返回值，直接检查恢复后的 State.variables
        var AV = SC.State.variables, after = {}, diffs = [];
        keys.forEach(function(k){
          try { after[k] = (AV[k]===undefined) ? "UNDEF" : (typeof AV[k]==="object" ? JSON.stringify(AV[k]).length : String(AV[k])); }
          catch(e){ after[k]="ERR"; }
          if (String(before[k]) !== String(after[k])) diffs.push({k:k,before:before[k],after:after[k]});
        });
        out.after = after;
        out.diffs = diffs;
        out.restoredPassage = SC.State.passage;
        out.objKeys = obj ? Object.keys(obj).slice(0,10) : null;
      }
      return out;
    } catch(e){ return { fatal: String(e.message||e).slice(0,300) }; }
  })())`);
  console.log(ser);

  try { ws.close(); } catch (e) { }
  try { proc.kill(); } catch (e) { }
  server.close();
  await sleep(600);
  try { fs.rmSync(PROFILE, { recursive: true, force: true }); } catch (e) { }
  try { fs.rmSync(WORK, { recursive: true, force: true }); } catch (e) { }
  process.exit(0);
})().catch(e => { console.error(e); process.exit(2); });
