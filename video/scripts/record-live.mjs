/**
 * Record simulated-user screen captures of https://repotruth.vercel.app
 * with visible cursor + click ripples. Outputs MP4 clips under video/captures/.
 */
import { chromium } from "playwright-core";
import fs from "fs";
import path from "path";
import { spawnSync } from "child_process";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, "..", "captures");
const BASE = process.env.BASE_URL || "https://repotruth.vercel.app";
const W = 1920;
const H = 1080;

fs.mkdirSync(OUT, { recursive: true });
fs.mkdirSync(path.join(OUT, "raw"), { recursive: true });

const CURSOR_JS = `
(() => {
  if (window.__demoCursor) return;
  window.__demoCursor = true;
  const style = document.createElement('style');
  style.textContent = \`
    #__demo_cursor {
      position: fixed; z-index: 2147483647; width: 22px; height: 22px;
      margin-left: -3px; margin-top: -3px; pointer-events: none;
      background: radial-gradient(circle at 30% 30%, #fff 0 18%, #7c5cff 22% 70%, transparent 72%);
      border: 2px solid #fff; border-radius: 50% 50% 50% 0; transform: rotate(-15deg);
      box-shadow: 0 2px 10px rgba(0,0,0,.45), 0 0 0 3px rgba(124,92,255,.35);
      transition: transform 40ms linear;
    }
    #__demo_cursor.clicking { transform: rotate(-15deg) scale(.82); }
    .__demo_ripple {
      position: fixed; z-index: 2147483646; width: 14px; height: 14px; border-radius: 50%;
      border: 2px solid rgba(124,92,255,.9); pointer-events: none;
      transform: translate(-50%,-50%) scale(1); opacity: .9;
      animation: __demo_ripple_anim .55s ease-out forwards;
    }
    @keyframes __demo_ripple_anim {
      to { transform: translate(-50%,-50%) scale(4.2); opacity: 0; }
    }
  \`;
  document.documentElement.appendChild(style);
  const cur = document.createElement('div');
  cur.id = '__demo_cursor';
  document.documentElement.appendChild(cur);
  let x = 40, y = 40;
  const move = (nx, ny) => { x = nx; y = ny; cur.style.left = x + 'px'; cur.style.top = y + 'px'; };
  window.addEventListener('mousemove', (e) => move(e.clientX, e.clientY), true);
  window.addEventListener('mousedown', (e) => {
    cur.classList.add('clicking');
    const r = document.createElement('div');
    r.className = '__demo_ripple';
    r.style.left = e.clientX + 'px';
    r.style.top = e.clientY + 'px';
    document.documentElement.appendChild(r);
    setTimeout(() => r.remove(), 600);
  }, true);
  window.addEventListener('mouseup', () => cur.classList.remove('clicking'), true);
  move(40, 40);
})();
`;

async function withPage(name, fn) {
  const browser = await chromium.launch({
    executablePath: "/usr/bin/google-chrome",
    args: ["--no-sandbox", "--disable-dev-shm-usage", "--hide-scrollbars", "--autoplay-policy=no-user-gesture-required"],
    headless: true,
  });
  const context = await browser.newContext({
    viewport: { width: W, height: H },
    deviceScaleFactor: 1,
    recordVideo: { dir: path.join(OUT, "raw"), size: { width: W, height: H } },
  });
  const page = await context.newPage();
  await page.addInitScript(CURSOR_JS);
  console.log(`[${name}] start`);
  try {
    await fn(page);
  } finally {
    const video = page.video();
    await context.close();
    await browser.close();
    if (video) {
      const vpath = await video.path();
      const webm = path.join(OUT, `${name}.webm`);
      const mp4 = path.join(OUT, `${name}.mp4`);
      fs.renameSync(vpath, webm);
      const r = spawnSync(
        "ffmpeg",
        ["-y", "-i", webm, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "18", "-an", mp4],
        { encoding: "utf8" },
      );
      if (r.status !== 0) {
        console.error(`[${name}] ffmpeg failed`, r.stderr?.slice(-500));
        throw new Error("ffmpeg failed for " + name);
      }
      const probe = spawnSync(
        "ffprobe",
        ["-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", mp4],
        { encoding: "utf8" },
      );
      console.log(`[${name}] ok duration=${(probe.stdout || "").trim()}s -> ${mp4}`);
    }
  }
}

async function humanMove(page, x, y, steps = 18) {
  await page.mouse.move(x, y, { steps });
}

async function humanClick(page, locator) {
  const box = await locator.boundingBox();
  if (!box) throw new Error("no box for click");
  const x = box.x + box.width * 0.5;
  const y = box.y + box.height * 0.55;
  await humanMove(page, x, y, 22);
  await page.waitForTimeout(180);
  await page.mouse.down();
  await page.waitForTimeout(70);
  await page.mouse.up();
  await page.waitForTimeout(250);
}

async function humanType(page, locator, text, delay = 55) {
  await locator.click({ clickCount: 3 }).catch(() => {});
  await page.waitForTimeout(200);
  await page.keyboard.press("Backspace").catch(() => {});
  await locator.fill("");
  await locator.focus();
  for (const ch of text) {
    await page.keyboard.type(ch, { delay: delay + Math.floor(Math.random() * 35) });
  }
}

async function shot(page, name) {
  const dest = path.join(OUT, `${name}.png`);
  await page.screenshot({ path: dest, fullPage: false });
  console.log("shot", dest);
}

// Clip 1: landing + scroll to auditor
await withPage("01-landing", async (page) => {
  await page.goto(BASE + "/", { waitUntil: "networkidle", timeout: 90000 });
  await page.waitForTimeout(1400);
  await shot(page, "shot-01-hero");
  await humanMove(page, 420, 280, 25);
  await page.waitForTimeout(900);
  // Move to Live auditor CTA
  const cta = page.locator('a.btn.primary[href="#auditor"]');
  await humanClick(page, cta);
  await page.waitForTimeout(1200);
  await shot(page, "shot-02-auditor");
  // Slow scroll to show stats / cards then auditor
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
  await page.waitForTimeout(400);
  for (const y of [180, 360, 520, 700, 900]) {
    await page.evaluate((yy) => window.scrollTo({ top: yy, behavior: "smooth" }), y);
    await page.waitForTimeout(700);
  }
  await page.locator("#auditor").scrollIntoViewIfNeeded();
  await page.waitForTimeout(1500);
  await humanMove(page, 700, 520, 20);
  await page.waitForTimeout(1800);
  await shot(page, "shot-03-auditor-form");
});

// Clip 2: fixture audit end-to-end (real Beam)
await withPage("02-audit", async (page) => {
  await page.goto(BASE + "/#auditor", { waitUntil: "networkidle", timeout: 90000 });
  await page.waitForTimeout(1200);
  await page.locator("#auditor").scrollIntoViewIfNeeded();
  await page.waitForTimeout(600);

  // Mode -> fixture
  const mode = page.locator("#mode");
  await humanClick(page, mode);
  await page.waitForTimeout(300);
  await mode.selectOption("fixture");
  await page.waitForTimeout(700);

  const fixture = page.locator("#fixture");
  await humanClick(page, fixture);
  await page.waitForTimeout(250);
  await fixture.selectOption("tinyclick");
  await page.waitForTimeout(500);

  const effort = page.locator("#effort");
  await humanClick(page, effort);
  await page.waitForTimeout(250);
  await effort.selectOption("low");
  await page.waitForTimeout(700);
  await shot(page, "shot-04-ready");

  const btn = page.locator("#auditBtn");
  await humanClick(page, btn);
  await page.waitForTimeout(400);
  await shot(page, "shot-05-calling");

  // Wait for LIVE findings
  await page.waitForFunction(
    () => {
      const s = document.getElementById("status");
      const f = document.getElementById("findings");
      return (
        s &&
        /LIVE Beam/i.test(s.textContent || "") &&
        f &&
        f.querySelectorAll(".finding").length >= 1
      );
    },
    { timeout: 90000 },
  );
  await page.waitForTimeout(1200);
  await shot(page, "shot-06-results");

  // Pause on thrift line, then scroll findings
  await humanMove(page, 640, 610, 18);
  await page.waitForTimeout(2200);
  await page.evaluate(() => {
    const f = document.getElementById("findings");
    if (f) f.scrollIntoView({ behavior: "smooth", block: "center" });
  });
  await page.waitForTimeout(1800);
  await page.evaluate(() => window.scrollBy({ top: 140, behavior: "smooth" }));
  await page.waitForTimeout(2200);
  await page.evaluate(() => window.scrollBy({ top: 160, behavior: "smooth" }));
  await page.waitForTimeout(2500);
  await shot(page, "shot-07-findings");
});

// Clip 3: GitHub mode — type a public URL (no second live call; show ready state)
await withPage("03-github", async (page) => {
  await page.goto(BASE + "/#auditor", { waitUntil: "networkidle", timeout: 90000 });
  await page.waitForTimeout(1000);
  await page.locator("#auditor").scrollIntoViewIfNeeded();
  await page.waitForTimeout(500);

  const mode = page.locator("#mode");
  await humanClick(page, mode);
  await mode.selectOption("github");
  await page.waitForTimeout(600);

  const effort = page.locator("#effort");
  await humanClick(page, effort);
  await effort.selectOption("low");
  await page.waitForTimeout(400);

  const github = page.locator("#github");
  await humanClick(page, github);
  await page.waitForTimeout(200);
  // Clear existing value then type slowly
  await github.fill("");
  await github.focus();
  const url = "https://github.com/pallets/itsdangerous";
  for (const ch of url) {
    await page.keyboard.type(ch, { delay: 42 + Math.floor(Math.random() * 28) });
  }
  await page.waitForTimeout(1200);
  await shot(page, "shot-08-github");

  // Hover the run button without clicking (avoid rate-limit burn; fixture already proved live)
  const btn = page.locator("#auditBtn");
  const box = await btn.boundingBox();
  if (box) await humanMove(page, box.x + box.width / 2, box.y + box.height / 2, 20);
  await page.waitForTimeout(2200);

  // Scroll featured verified findings for judges
  await page.evaluate(() => window.scrollBy({ top: 420, behavior: "smooth" }));
  await page.waitForTimeout(2500);
  await page.evaluate(() => window.scrollBy({ top: 280, behavior: "smooth" }));
  await page.waitForTimeout(2200);
  await shot(page, "shot-09-featured");
});

console.log("ALL CLIPS DONE");
