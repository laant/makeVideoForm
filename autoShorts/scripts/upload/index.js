// 업로드. 기본은 dry-run(무엇을 올릴지 출력만). 실제 업로드는 --yes
//   npm run upload -- <slug> [--yes] [--only youtube|instagram] [--again]
import "../lib/env.js";
import fs from "node:fs";
import path from "node:path";
import { ROOT, episodePaths } from "../lib/paths.js";
import { loadEpisode, slugArg, hasFlag } from "../lib/episode.js";
import { run } from "../lib/proc.js";
import { youtubeReady, youtubeMeta, uploadYouTube } from "./youtube.js";
import { instagramReady, instagramCaption, uploadInstagram } from "./instagram.js";

const slug = slugArg();
const ep = loadEpisode(slug);
const P = episodePaths(slug);
const YES = hasFlag("yes");
const onlyIdx = process.argv.indexOf("--only");
const only = onlyIdx > 0 ? process.argv[onlyIdx + 1] : null;

// 업로드 전 기술 검수 재실행 (실패 시 중단)
await run(process.execPath, [path.join(ROOT, "scripts/verify.js"), slug]);

const log = fs.existsSync(P.uploadLog) ? JSON.parse(fs.readFileSync(P.uploadLog, "utf8")) : {};
const targets = [
  { key: "youtube", enabled: ep.upload.youtube, ready: youtubeReady, preview: () => youtubeMeta(ep), upload: uploadYouTube },
  { key: "instagram", enabled: ep.upload.instagram, ready: instagramReady, preview: () => ({ caption: instagramCaption(ep) }), upload: uploadInstagram },
].filter((t) => t.enabled && (!only || only === t.key));

let failed = false;
for (const t of targets) {
  console.log(`\n── ${t.key} ──`);
  console.log(JSON.stringify(t.preview(), null, 2));
  if (log[t.key] && !hasFlag("again")) {
    console.log(`= 이미 업로드됨: ${log[t.key].url} (다시 올리려면 --again)`);
    continue;
  }
  const missing = t.ready();
  if (missing.length) {
    console.warn(`⚠ 설정 누락: ${missing.join(", ")}`);
    failed = true;
    continue;
  }
  if (!YES) {
    console.log("(dry-run) 실제 업로드하려면 --yes");
    continue;
  }
  try {
    const result = await t.upload(ep, P.final);
    log[t.key] = { ...result, at: new Date().toISOString() };
    fs.writeFileSync(P.uploadLog, JSON.stringify(log, null, 2));
    console.log(`✓ ${t.key}: ${result.url ?? result.id}`);
  } catch (e) {
    console.error(`✗ ${t.key}: ${e.message}`);
    failed = true;
  }
}
if (failed) process.exit(1);
