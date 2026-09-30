// 네이버 클립 업로드 준비 · 기록 — 업로드 자체는 Claude 가 Aside 브라우저로 clipcreators.naver.com 폼을 채운다
// (네이버 클립은 공개 업로드 API 없음. 절차: ../../docs/naver-clip.md)
//
//   npm run clip -- <프로젝트> --module <모듈> [--title N] [--thumb 1|2] [--session <Aside 세션 폴더>]
//       → 영상·커버를 Aside 세션 폴더 upload/ 로 복사(Aside 는 세션 폴더 밖 파일을 못 올림)
//       → titles.txt(★ 기본)로 300자 설명 생성 → output/<프로젝트>/naverclip-plan.json
//   npm run clip -- <프로젝트> --module <모듈> --log [--url <클립 주소>]
//       → publish-log.json 에 naverclip 기록 (등록 후)
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { ROOT } from "../lib/paths.js";

const OUTPUT = path.resolve(ROOT, "..", "output");
const MAX = 300;
const argv = process.argv.slice(2);
const opt = (n) => (argv.includes(`--${n}`) ? argv[argv.indexOf(`--${n}`) + 1] : undefined);
const VALUE_OPTS = ["module", "title", "thumb", "session", "url"];
const project = argv.find((a, i) => !a.startsWith("-") && !VALUE_OPTS.includes(argv[i - 1]?.replace(/^--/, "")));
const die = (m) => (console.error(`✗ ${m}`), process.exit(1));

if (!project) die("사용법: npm run clip -- <프로젝트> --module <모듈> [--log --url <주소>]");
const dir = path.join(OUTPUT, project);
const module = opt("module") || die("--module 을 지정하세요");
const video = path.join(dir, `${module}_final_send.mp4`);
if (!fs.existsSync(video)) die(`영상 없음: ${path.relative(OUTPUT, video)}`);
const logFile = path.join(dir, "publish-log.json");
const planFile = path.join(dir, "naverclip-plan.json");

if (argv.includes("--log")) {
  const log = fs.existsSync(logFile) ? JSON.parse(fs.readFileSync(logFile, "utf8")) : {};
  const plan = fs.existsSync(planFile) ? JSON.parse(fs.readFileSync(planFile, "utf8")) : {};
  if (log.naverclip) log.naverclipHistory = [...(log.naverclipHistory ?? []), log.naverclip];
  log.naverclip = { module, titleNo: plan.titleNo ?? null, title: plan.title ?? null, url: opt("url") ?? null, profile: "https://clip.naver.com/@some____uuuu", at: new Date().toISOString() };
  fs.writeFileSync(logFile, JSON.stringify(log, null, 2));
  console.log(`✓ publish-log.json naverclip 기록${opt("url") ? `: ${opt("url")}` : ""}`);
  process.exit(0);
}

// ── titles.txt → 300자 설명 ─────────────────────────────────
function parseTitles(file) {
  const entries = [];
  let cur = null, inDesc = false, star = null;
  for (const line of fs.readFileSync(file, "utf8").split("\n")) {
    const m = line.match(/^(\d+)\. 제목\(\d+자\): (.+)$/);
    if (m) { cur = { no: Number(m[1]), title: m[2].trim(), desc: [] }; entries.push(cur); inDesc = false; continue; }
    const s = line.match(/^★ 가장 바이럴 가능성 높은 제목: (.+)$/);
    if (s) star = s[1].trim();
    if (/^(■|=+|★)/.test(line)) { cur = null; continue; }
    if (!cur) continue;
    if (/^\s+설명\(\d+자\):/.test(line)) { inDesc = true; continue; }
    if (inDesc) cur.desc.push(line.replace(/^ {3}/, ""));
  }
  return { entries, star };
}

const titlesFile = path.join(dir, "titles.txt");
if (!fs.existsSync(titlesFile)) die(`titles.txt 없음: output/${project}/titles.txt`);
const { entries, star } = parseTitles(titlesFile);
const entry = opt("title") ? entries.find((e) => e.no === Number(opt("title"))) : entries.find((e) => e.title === star) ?? entries[0];
if (!entry) die("titles.txt 에서 제목을 찾지 못했습니다");

const lines = entry.desc.map((l) => l.trim()).filter(Boolean);
const tags = (lines.reverse().find((l) => l.startsWith("#")) ?? "").split(/\s+/).filter((t) => t.startsWith("#")).slice(0, 5);
lines.reverse();
const body = lines.filter((l) => l !== entry.title && !l.startsWith("#") && !l.startsWith("※") && !/https?:\/\//.test(l));
const notes = lines.filter((l) => l.startsWith("※")).map((l) => l.split(/(?<=[.요다])\s/)[0]); // 고지 문장은 첫 문장만
const hasLink = lines.some((l) => /https?:\/\//.test(l));

function build(nBody) {
  return [entry.title, ...body.slice(0, nBody), hasLink ? "자세한 내용은 연결된 블로그 글에서 확인하세요." : null, ...notes, tags.join(" ")]
    .filter(Boolean).join("\n");
}
let n = body.length;
let description = build(n);
while (description.length > MAX && n > 0) description = build(--n);
if (description.length > MAX) description = description.slice(0, MAX);

// ── Aside 세션 폴더로 복사 ─────────────────────────────────
function latestSession() {
  const base = path.join(os.homedir(), ".aside/u/0/sessions");
  if (!fs.existsSync(base)) return null;
  const ds = fs.readdirSync(base).map((d) => path.join(base, d)).filter((d) => fs.statSync(d).isDirectory());
  return ds.sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs)[0] ?? null;
}
const session = opt("session") || latestSession() || die("Aside 세션 폴더를 찾지 못했습니다 — REPL 에서 pwd() 결과를 --session 으로 주세요");
const up = path.join(session, "upload");
fs.mkdirSync(up, { recursive: true });
const vName = `${project}.mp4`;
fs.copyFileSync(video, path.join(up, vName));
const thumbSrc = path.join(dir, `${module}_final_send_thumb${opt("thumb") ?? "1"}.jpg`);
const tName = fs.existsSync(thumbSrc) ? `${project}-thumb.jpg` : null;
if (tName) fs.copyFileSync(thumbSrc, path.join(up, tName));

const plan = {
  project, module, titleNo: entry.no, title: entry.title,
  session, video: `upload/${vName}`, cover: tName ? `upload/${tName}` : null,
  description, length: description.length,
  hints: {
    aiUse: "AI 음성·생성 이미지를 썼으면 켬",
    shoppingConnect: "쇼핑 영상이면 정보 태그 '쇼핑커넥트'에서 상품 1개 선택(카테고리당 1개) → 광고·협찬 자동 켜짐",
    blogLink: hasLink ? "콘텐츠 링크 '블로그'에서 원문 글 선택(내 블로그 글만)" : null,
  },
};
fs.writeFileSync(planFile, JSON.stringify(plan, null, 2));
console.log(`▶ ${project} / ${module} → 네이버 클립`);
console.log(`  제목 #${entry.no}${entry.title === star ? " ★" : ""}: ${entry.title}`);
console.log(`  Aside 세션: ${session}`);
console.log(`  첨부: ${plan.video}${plan.cover ? ` · 커버 ${plan.cover}` : ""}`);
console.log(`  설명 (${description.length}/${MAX}자):\n${description.replace(/^/gm, "    ")}`);
console.log(`✓ output/${project}/naverclip-plan.json — 등록 후: npm run clip -- ${project} --module ${module} --log --url <주소>`);
