// myNextSeason 완성본 배포: output/<프로젝트>/<모듈>_final_send.mp4 → YouTube Shorts · Instagram Reels
// 제목·설명은 output/<프로젝트>/titles.txt (기본 ★바이럴 1순위), 썸네일은 <모듈>_final_send_thumb1.jpg.
// 기본은 dry-run(무엇을 올릴지 출력만). 실제 업로드는 --yes (사용자가 요청했을 때만)
//
//   npm run publish -- <프로젝트> --module <모듈> [--title <번호>] [--thumb 1|2|none]
//                      [--only youtube|instagram] [--at "YYYY-MM-DD HH:mm"] [--privacy private|unlisted|public]
//                      [--yes] [--again]
//
//   --at     YouTube 예약 공개(한국 시간). 비공개로 올린 뒤 그 시각에 공개. Instagram은 예약이 없어 건너뜀
//   --again  같은 프로젝트를 같은 플랫폼에 이미 올렸어도 다시 올림 (모듈판이 달라도 채널 중복 방지가 기본)
import "./lib/env.js";
import fs from "node:fs";
import path from "node:path";
import { ROOT } from "./lib/paths.js";
import { ffprobeJson } from "./lib/proc.js";
import { youtubeReady, uploadYouTubeWith, youtubeChannel, youtubeTokenAgeDays, explainAuthError } from "./upload/youtube.js";
import { instagramReady, uploadInstagramWith } from "./upload/instagram.js";

const OUTPUT = path.resolve(ROOT, "..", "output");
const argv = process.argv.slice(2);
const opt = (name) => {
  const i = argv.indexOf(`--${name}`);
  return i >= 0 ? argv[i + 1] : undefined;
};
const flag = (name) => argv.includes(`--${name}`);
const VALUE_OPTS = ["module", "title", "thumb", "only", "at", "privacy"];
const project = argv.find((a, i) => !a.startsWith("-") && !VALUE_OPTS.includes(argv[i - 1]?.replace(/^--/, "")));

function die(msg) {
  console.error(`✗ ${msg}`);
  process.exit(1);
}

if (!project) {
  const list = fs.existsSync(OUTPUT) ? fs.readdirSync(OUTPUT).filter((d) => fs.existsSync(path.join(OUTPUT, d, "titles.txt"))) : [];
  die(`사용법: npm run publish -- <프로젝트> --module <모듈> [--yes]\n  titles.txt 있는 프로젝트: ${list.join(", ") || "(없음)"}`);
}
const dir = path.join(OUTPUT, project);
if (!fs.existsSync(dir)) die(`프로젝트 없음: output/${project}`);

// ── 모듈판 선택 ─────────────────────────────────────────────
const modules = fs.readdirSync(dir).filter((f) => f.endsWith("_final_send.mp4")).map((f) => f.replace("_final_send.mp4", ""));
const module = opt("module");
if (!module) die(`--module 을 지정하세요. 이 프로젝트의 모듈판: ${modules.join(", ")}`);
if (!modules.includes(module)) die(`모듈판 없음: ${module} (가능: ${modules.join(", ")})`);
const video = path.join(dir, `${module}_final_send.mp4`);

// ── titles.txt 파싱 ────────────────────────────────────────
// 형식: "N. 제목(n자): …" 다음 "   설명(n자):" 와 3칸 들여쓴 본문, 마지막에 "★ 가장 바이럴 가능성 높은 제목: …"
function parseTitles(file) {
  const lines = fs.readFileSync(file, "utf8").split("\n");
  const entries = [];
  let cur = null;
  let inDesc = false;
  let star = null;
  for (const line of lines) {
    const m = line.match(/^(\d+)\. 제목\(\d+자\): (.+)$/);
    if (m) {
      cur = { no: Number(m[1]), title: m[2].trim(), desc: [] };
      entries.push(cur);
      inDesc = false;
      continue;
    }
    const s = line.match(/^★ 가장 바이럴 가능성 높은 제목: (.+)$/);
    if (s) star = s[1].trim();
    if (/^(■|=+|★)/.test(line)) {
      cur = null;
      continue;
    }
    if (!cur) continue;
    if (/^\s+설명\(\d+자\):/.test(line)) {
      inDesc = true;
      continue;
    }
    if (inDesc) cur.desc.push(line.replace(/^ {3}/, ""));
  }
  for (const e of entries) {
    e.description = e.desc.join("\n").trim();
    delete e.desc;
    const tagLine = e.description.split("\n").reverse().find((l) => l.trim().startsWith("#")) ?? "";
    e.hashtags = tagLine.trim().split(/\s+/).filter((h) => h.startsWith("#"));
  }
  return { entries, star };
}

const titlesFile = path.join(dir, "titles.txt");
if (!fs.existsSync(titlesFile)) die(`titles.txt 없음: output/${project}/titles.txt (PRODUCTION.md 업로드 준비물 규칙)`);
const { entries, star } = parseTitles(titlesFile);
if (!entries.length) die("titles.txt 에서 제목을 찾지 못했습니다 (형식 확인)");
const titleNo = opt("title");
const entry = titleNo ? entries.find((e) => e.no === Number(titleNo)) : entries.find((e) => e.title === star);
if (!entry) die(titleNo ? `제목 번호 없음: ${titleNo} (1~${entries.length})` : "★ 제목을 찾지 못했습니다 — --title <번호> 로 지정하세요");

// ── 썸네일 · 영상 검사 ─────────────────────────────────────
const thumbOpt = opt("thumb") ?? "1";
const thumbnail = thumbOpt === "none" ? null : path.join(dir, `${module}_final_send_thumb${thumbOpt}.jpg`);
if (thumbnail && !fs.existsSync(thumbnail)) die(`썸네일 없음: ${path.basename(thumbnail)} (--thumb none 으로 생략 가능)`);

const probe = ffprobeJson(video);
const v = probe.streams.find((s) => s.codec_type === "video");
const duration = Number(probe.format.duration);
const vertical = v && v.height > v.width;
const warnings = [];
if (!vertical) warnings.push(`가로 영상(${v?.width}x${v?.height}) — YouTube Shorts·Reels 가 아닌 일반 영상으로 분류됩니다`);
if (duration > 180) warnings.push(`${duration.toFixed(1)}초 — 3분 초과라 YouTube Shorts 로 분류되지 않습니다`);
if (!probe.streams.some((s) => s.codec_type === "audio")) warnings.push("오디오 스트림 없음");

// ── 예약 시각 ──────────────────────────────────────────────
let publishAt = null;
if (opt("at")) {
  const m = opt("at").match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})$/);
  if (!m) die('--at 형식: "YYYY-MM-DD HH:mm" (한국 시간)');
  const d = new Date(`${m[1]}-${m[2]}-${m[3]}T${m[4]}:${m[5]}:00+09:00`);
  if (d.getTime() < Date.now() + 15 * 60 * 1000) die("--at 은 지금부터 15분 이후여야 합니다");
  publishAt = d.toISOString();
}
const privacy = opt("privacy") || process.env.YT_PRIVACY || "private";
if (!["private", "unlisted", "public"].includes(privacy)) die(`--privacy 값 오류: ${privacy}`);

// ── 대상 플랫폼 ────────────────────────────────────────────
const only = opt("only");
if (only && !["youtube", "instagram"].includes(only)) die(`--only 값 오류: ${only}`);
const tags = [];
for (const h of entry.hashtags.map((h) => h.replace(/^#/, ""))) {
  if (tags.length >= 15 || tags.join(",").length + h.length > 450) break;
  tags.push(h);
}
const ytMeta = {
  title: entry.title.slice(0, 100),
  description: entry.description.slice(0, 5000),
  tags,
  privacyStatus: publishAt ? "private" : privacy,
  ...(publishAt && { publishAt }),
};
const igCaption = entry.description.slice(0, 2200);

const logFile = path.join(dir, "publish-log.json");
const log = fs.existsSync(logFile) ? JSON.parse(fs.readFileSync(logFile, "utf8")) : {};
const YES = flag("yes");

const targets = [
  {
    key: "youtube",
    ready: youtubeReady,
    preview: { ...ytMeta, description: `${ytMeta.description.slice(0, 120)}… (${ytMeta.description.length}자)`, thumbnail: thumbnail && path.basename(thumbnail) },
    upload: () => uploadYouTubeWith(ytMeta, video, { thumbnail }),
    // 토큰 채널이 .env YT_CHANNEL_HANDLE 과 다르면 중단 (개인 채널 오업로드 방지)
    precheck: async () => {
      const age = youtubeTokenAgeDays();
      if (age !== null && age > 6) console.warn(`  ⚠ 토큰 발급 ${age.toFixed(1)}일 경과 — OAuth '테스트' 상태면 7일에 만료됩니다 (npm run yt:auth)`);
      const ch = await youtubeChannel();
      console.log(`  채널: ${ch.title} ${ch.handle ?? ""}`);
      const want = process.env.YT_CHANNEL_HANDLE?.trim().toLowerCase();
      if (!want) return "YT_CHANNEL_HANDLE 미설정 — .env 에 올릴 채널 핸들(@…)을 적으세요";
      if ((ch.handle ?? "").toLowerCase() !== want) return `채널 불일치: 토큰=${ch.handle ?? ch.title}, 설정=${want} — npm run yt:auth 에서 브랜드 채널을 선택하세요`;
      return null;
    },
  },
  {
    key: "instagram",
    ready: instagramReady,
    skip: publishAt ? "--at 예약은 YouTube 전용 (Instagram API 에 예약 게시 없음) — 공개 시각에 --only instagram 으로 따로 올리세요" : null,
    preview: { caption: `${igCaption.slice(0, 120)}… (${igCaption.length}자)`, note: "릴스 커버는 영상 1.2초 프레임" },
    upload: () => uploadInstagramWith(igCaption, video),
  },
].filter((t) => !only || only === t.key);

console.log(`▶ ${project} / ${module}  (${v?.width}x${v?.height}, ${duration.toFixed(1)}s)`);
console.log(`  제목 #${entry.no}${entry.title === star ? " ★" : ""}: ${entry.title}`);
for (const w of warnings) console.warn(`  ⚠ ${w}`);

let failed = false;
for (const t of targets) {
  console.log(`\n── ${t.key} ──`);
  console.log(JSON.stringify(t.preview, null, 2));
  if (t.skip) {
    console.log(`= 건너뜀: ${t.skip}`);
    continue;
  }
  if (log[t.key] && !flag("again")) {
    const prev = log[t.key];
    console.log(`= 이미 게시됨: ${prev.module}판 ${prev.url ?? prev.id} (${prev.at}) — 다시 올리려면 --again`);
    continue;
  }
  const missing = t.ready();
  if (missing.length) {
    console.warn(`⚠ 설정 누락: ${missing.join(", ")}`);
    failed = true;
    continue;
  }
  if (t.precheck) {
    let problem;
    try {
      problem = await t.precheck();
    } catch (e) {
      problem = explainAuthError(e);
    }
    if (problem) {
      console.warn(`⚠ ${problem}`);
      failed = true;
      continue;
    }
  }
  if (!YES) {
    console.log("(dry-run) 실제 업로드하려면 --yes");
    continue;
  }
  try {
    const result = await t.upload();
    log[t.key] = { module, titleNo: entry.no, title: entry.title, ...result, at: new Date().toISOString() };
    fs.writeFileSync(logFile, JSON.stringify(log, null, 2));
    console.log(`✓ ${t.key}: ${result.url ?? result.id}${result.publishAt ? ` (예약 공개 ${result.publishAt})` : ""}`);
  } catch (e) {
    console.error(`✗ ${t.key}: ${t.key === "youtube" ? explainAuthError(e) : e.message}`);
    failed = true;
  }
}
if (failed) process.exit(1);
