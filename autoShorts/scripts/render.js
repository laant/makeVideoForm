// scenes/sNN.html → renders/sNN.mp4 (HyperFrames). 씬 HTML 이 mp4 보다 새로울 때만 렌더.
//   npm run render -- <slug> [--force] [--only s02] [--draft]
import fs from "node:fs";
import path from "node:path";
import { episodePaths } from "./lib/paths.js";
import { loadEpisode, requireTiming, renderDurationOf, slugArg, hasFlag } from "./lib/episode.js";
import { HF_BIN, run, mediaDuration } from "./lib/proc.js";

const slug = slugArg();
const ep = loadEpisode(slug);
requireTiming(ep);
const P = episodePaths(slug);
const FORCE = hasFlag("force");
const onlyIdx = process.argv.indexOf("--only");
const only = onlyIdx > 0 ? process.argv[onlyIdx + 1] : null;
fs.mkdirSync(P.renders, { recursive: true });

// 미리보기 합본 lint (에러 시 중단)
await run(HF_BIN, ["lint", "."], { cwd: P.dir });

for (const [i, scene] of ep.scenes.entries()) {
  if (only && scene.id !== only) continue;
  const html = path.join(P.scenes, `${scene.id}.html`);
  const mp4 = path.join(P.renders, `${scene.id}.mp4`);
  if (!fs.existsSync(html)) throw new Error(`${html} 없음 → npm run scenes -- ${slug}`);
  const expected = renderDurationOf(ep, i);
  const fresh =
    fs.existsSync(mp4) &&
    fs.statSync(mp4).mtimeMs > fs.statSync(html).mtimeMs &&
    Math.abs(mediaDuration(mp4) - expected) < 0.1;
  if (fresh && !FORCE) {
    console.log(`= ${scene.id} 최신 렌더 있음`);
    continue;
  }
  const custom = fs.readFileSync(html, "utf8").includes("autoshorts:custom");
  if (custom && !fs.readFileSync(html, "utf8").includes(`data-duration="${expected}"`)) {
    console.warn(`⚠ ${scene.id} custom 씬의 data-duration 이 ${expected}s 와 다릅니다 — 싱크가 어긋날 수 있음`);
  }
  console.log(`▶ ${scene.id} 렌더 (${expected}s)`);
  const args = ["render", ".", "-c", `scenes/${scene.id}.html`, "-o", mp4, "--strict", "--quiet", "--fps", "30"];
  if (hasFlag("draft")) args.push("--quality", "draft");
  await run(HF_BIN, args, { cwd: P.dir });
}
console.log("✓ 렌더 완료");
