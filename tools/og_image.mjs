// Renders the social preview image web/og.png (1200x630) and the raster logo web/logo-512.png
// from the SVG logo with the installed Chrome (Playwright). Run after tools/build_logo.py:
//
//   PW_CHANNEL=chrome node tools/og_image.mjs
//
// Both PNGs are committed; this only needs to run when the logo or the claim changes.
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";
import { dirname, join } from "node:path";
import { writeFileSync, unlinkSync } from "node:fs";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const scratch = process.env.PYODIDE_DIR || join(root, ".local", "pyodide-test");
const { chromium } = createRequire(join(scratch, "package.json"))("playwright");

const card = join(root, "web", "_og.html");
writeFileSync(card, `<!doctype html><html><head><meta charset="utf-8"><style>
  @font-face { font-family: Inter; src: url("fonts/inter-latin.woff2") format("woff2"); font-weight: 400 700; }
  html, body { margin: 0; }
  body { width: 1200px; height: 630px; font-family: Inter, system-ui, sans-serif; color: #12305b;
         background: linear-gradient(135deg, #f4f6f8 0%, #e4ecf9 55%, #d9f1ee 100%); position: relative; overflow: hidden; }
  .logo { position: absolute; left: 88px; top: 96px; width: 620px; }
  .claim { position: absolute; left: 92px; top: 330px; font-size: 44px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.15; max-width: 1020px; }
  .sub { position: absolute; left: 92px; top: 470px; font-size: 24px; color: #5b6b83; max-width: 1000px; line-height: 1.4; }
  .url { position: absolute; right: 88px; bottom: 44px; font-size: 22px; font-weight: 600; color: #1c4f9e; }
</style></head><body>
  <img class="logo" src="logo.svg" alt="">
  <div class="claim">CRS-Meldungen an die ESTV. Geprüft, verschlüsselt, bereit zum Hochladen.</div>
  <div class="sub">Im Browser, ohne Installation. Ihre Kontodaten verlassen Ihren Rechner nicht. Deutsch · Français · Italiano</div>
  <div class="url">meldbar.ch</div>
</body></html>`);
const tile = join(root, "web", "_logo.html");
writeFileSync(tile, `<!doctype html><html><body style="margin:0;width:512px;height:512px;background:#fff;display:grid;place-items:center">
  <img src="logo-mark.svg" style="width:400px;height:400px"></body></html>`);

const browser = await chromium.launch(process.env.PW_CHANNEL ? { channel: process.env.PW_CHANNEL } : {});
try {
  const og = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  await og.goto(pathToFileURL(card).href);
  await og.waitForTimeout(400);
  await og.screenshot({ path: join(root, "web", "og.png") });
  const lg = await browser.newPage({ viewport: { width: 512, height: 512 }, deviceScaleFactor: 1 });
  await lg.goto(pathToFileURL(tile).href);
  await lg.waitForTimeout(300);
  await lg.screenshot({ path: join(root, "web", "logo-512.png") });
} finally {
  await browser.close();
  unlinkSync(card);
  unlinkSync(tile);
}
console.log("wrote web/og.png (1200x630) and web/logo-512.png");
