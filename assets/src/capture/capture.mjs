// Make the pictures the README graphics are cut from, with headless Chrome (WebGL on):
// words set in the site's typeface, and still frames of the site's 3D figure.
//
//   node assets/src/capture/capture.mjs <folder of the portfolio site> [job ...]
//
// Jobs: words, guide-header, guide-terminal, guide-poses. With none named, all four run.
// Each job opens the page of the same name beside this file and saves its pictures into
// ../pictures/<job>/. Afterwards run  python assets/src/build.py  to redraw the graphics.
//
// The site folder is needed because the figure is drawn by the site's own js/guide.js.
// The words page takes Bricolage Grotesque from Google Fonts, so it needs the network.
// Chrome is looked for in the usual places; set CHROME to the full path of another one.
//
// A page sets window.ready = true and window.targets = [{ id, x, y, w, h, ... }];
// an optional async window.before(id) runs before each picture is taken.
import { spawn } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import { createServer } from "node:http";
import { tmpdir } from "node:os";
import { dirname, extname, join, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const PICTURES = resolve(HERE, "..", "pictures");
// dpr: how many picture pixels to one page pixel. clear: keep the background transparent. w, h: the window.
const JOBS = {
  "words": { dpr: 2, clear: false, w: 2400, h: 1200 },
  "guide-header": { dpr: 2, clear: true, w: 600, h: 400 },
  "guide-terminal": { dpr: 1.5, clear: true, w: 600, h: 400 },
  "guide-poses": { dpr: 2, clear: true, w: 600, h: 600 }
};
const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".mjs": "text/javascript", ".css": "text/css", ".json": "application/json" };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const [siteArg, ...asked] = process.argv.slice(2);
const site = siteArg ? resolve(siteArg) : "";
if (!site || !existsSync(join(site, "js", "guide.js"))) {
  console.error("Give the folder of the portfolio site, the one that holds js/guide.js:\n  node assets/src/capture/capture.mjs <folder> [job ...]");
  process.exit(1);
}
const jobs = asked.length ? asked : Object.keys(JOBS);
const unknown = jobs.find((j) => !JOBS[j]);
if (unknown) {
  console.error(`No job is called ${unknown}. The jobs are: ${Object.keys(JOBS).join(", ")}`);
  process.exit(1);
}
const chrome = [
  process.env.CHROME,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/usr/bin/google-chrome",
  "/usr/bin/chromium",
  "/usr/bin/chromium-browser"
].find((p) => p && existsSync(p));
if (!chrome) {
  console.error("Chrome was not found. Set CHROME to its full path.");
  process.exit(1);
}

// One small server: this folder at /, the site at /site/, so a page and the site's code share an origin.
function serve() {
  const server = createServer((req, res) => {
    const path = decodeURIComponent(new URL(req.url, "http://localhost").pathname);
    const [root, rel] = path.startsWith("/site/") ? [site, path.slice(6)] : [HERE, path.slice(1)];
    const file = resolve(root, rel);
    if (!file.startsWith(root + sep) || !existsSync(file) || !statSync(file).isFile()) {
      res.writeHead(404);
      res.end();
      return;
    }
    res.writeHead(200, { "content-type": TYPES[extname(file)] || "application/octet-stream" });
    res.end(readFileSync(file));
  });
  return new Promise((done) => server.listen(0, "127.0.0.1", () => done(server)));
}

async function capture(job, url) {
  const { dpr, clear, w, h } = JOBS[job];
  const outDir = join(PICTURES, job);
  mkdirSync(outDir, { recursive: true });
  const profile = mkdtempSync(join(tmpdir(), "cap-"));
  const child = spawn(chrome, [
    "--headless=new", "--remote-debugging-port=0", `--user-data-dir=${profile}`, "--hide-scrollbars", "--no-first-run",
    "--enable-unsafe-swiftshader", "--use-angle=swiftshader", "--ignore-gpu-blocklist", `--window-size=${w},${h}`, "about:blank"
  ]);
  try {
    const browserWs = await new Promise((res, rej) => {
      let buf = "";
      child.stderr.on("data", (d) => { buf += d; const m = buf.match(/DevTools listening on (ws:\/\/\S+)/); if (m) res(m[1]); });
      setTimeout(() => rej(new Error("Chrome did not report a debugging address")), 20000);
    });
    const port = new URL(browserWs).port;
    let page;
    for (let i = 0; i < 40 && !page; i++) {
      const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
      page = list.find((t) => t.type === "page");
      if (!page) await sleep(250);
    }
    const ws = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise((r) => (ws.onopen = r));
    let id = 0;
    const waiting = new Map();
    ws.onmessage = (m) => {
      const msg = JSON.parse(m.data);
      if (msg.id && waiting.has(msg.id)) { waiting.get(msg.id)(msg); waiting.delete(msg.id); }
    };
    const send = (method, params = {}) => new Promise((res) => { waiting.set(++id, res); ws.send(JSON.stringify({ id, method, params })); });
    const evaluate = async (expression) => (await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true })).result?.result?.value;

    await send("Page.enable");
    await send("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: dpr, mobile: false });
    if (clear) await send("Emulation.setDefaultBackgroundColorOverride", { color: { r: 0, g: 0, b: 0, a: 0 } });
    await send("Page.navigate", { url });
    let ready = false;
    for (let i = 0; i < 120 && !ready; i++) { await sleep(250); ready = await evaluate("window.ready === true"); }
    if (!ready) throw new Error(`${job}: the page never became ready`);
    const targets = JSON.parse(await evaluate("JSON.stringify(window.targets)"));
    for (const t of targets) {
      await evaluate(`window.before ? window.before(${JSON.stringify(t.id)}) : null`);
      const shot = await send("Page.captureScreenshot", {
        format: "png", captureBeyondViewport: true,
        clip: { x: t.x, y: t.y, width: t.w, height: t.h, scale: 1 }
      });
      writeFileSync(join(outDir, t.id + ".png"), Buffer.from(shot.result.data, "base64"));
    }
    writeFileSync(join(outDir, "targets.json"), JSON.stringify({ dpr, targets }, null, 1));
    console.log(`${job}: saved ${targets.length} pictures`);
    ws.close();
  } finally {
    child.kill();
    await sleep(400);
    try { rmSync(profile, { recursive: true, force: true }); } catch {}
  }
}

const server = await serve();
try {
  for (const job of jobs) await capture(job, `http://127.0.0.1:${server.address().port}/${job}.html`);
} finally {
  server.close();
}
