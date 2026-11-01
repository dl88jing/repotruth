import { chromium } from "playwright-core";
import fs from "fs";
import path from "path";
import { spawnSync } from "child_process";
import { fileURLToPath } from "url";
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, "..", "captures");
const BASE = "https://repotruth.vercel.app";
const W=1920,H=1080;
const CURSOR_JS = fs.readFileSync(path.join(__dirname,'record-live.mjs'),'utf8').match(/const CURSOR_JS = `([\s\S]*?)`;/)[1];
// Actually embed again:
