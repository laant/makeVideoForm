// 업로드. 기본은 dry-run(무엇을 올릴지 출력만). 실제 업로드는 --yes
//   npm run upload -- <slug> [--yes] [--only youtube|instagram] [--again] [--skip-precheck]
import "../lib/env.js";
import fs from "node:fs";
import path from "node:path";
import { ROOT, episodePaths } from "../lib/paths.js";
import { loadEpisode, slugArg, hasFlag } from "../lib/episode.js";
import { run } from "../lib/proc.js";
import { youtubeReady, youtubeMeta, uploadYouTube } from "./youtube.js";
import { instagramReady, instagramCaption, uploadInstagram } from "./instagram.js";
import { precheck, printPrecheck, strings } from "../lib/precheck.js";

const slug = slugArg();
const ep = loadEpisode(slug);
const P = episodePaths(slug);
const YES = hasFlag("yes");
const onlyIdx = process.argv.indexOf("--only");
const only = onlyIdx > 0 ? process.argv[onlyIdx + 1] : null;

// 업로드 전 기술 검수 재실행 (실패 시 중단)
await run(process.execPath, [path.join(ROOT, "scripts/verify.js"), slug]);

// 업로드 전 점검 (링크·자리표시자·URL) — ✗ 가 있으면 --yes 여도 중단, --skip-precheck 로만 통과
const yt = youtubeMeta(ep);
const igCaption = [ep.caption, "", ep.hashtags.join(" ")].join("\n").trim();
const pre = await precheck({
  texts: [
    ...ep.scenes.flatMap((s) => [...strings(s.onScreen, `${s.id}.onScreen`), { where: `${s.id}.narration`, text: s.narration }]),
    { where: "caption", text: ep.caption },
    { where: "upload.title", text: ep.upload.title },
  ],
  spoken: ep.scenes.map((s) => s.narration),
  description: yt.description,
  limits: [
    { where: "YouTube 제목", text: `${ep.upload.title || ep.topic} #Shorts`, max: 100 },
    { where: "Instagram 캡션", text: igCaption, max: 2200 },
  ],
});
printPrecheck(pre);
const BLOCKED = pre.fails.length > 0 && !hasFlag("skip-precheck");
if (BLOCKED) console.log("✗ 업로드 전 점검 실패 — 고친 뒤 다시 실행 (무시하려면 --skip-precheck)");

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
  if (BLOCKED) {
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
