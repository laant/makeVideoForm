// source.json 의 상품 이미지(공개 URL) → Higgsfield image-to-video → episodes/<slug>/media/<key>.mp4
//   npm run clips -- <slug> [--dry] [--force] [--only p01-hero] [--model dop-lite] [--strength 0.35]
//
// 멱등: media/clips.json 에 기록이 있고 mp4 가 있으면 건너뛴다(--force 로 재생성).
// 상품 원형 보존이 최우선이라 기본값은 SAFE_DEFAULTS (약한 모션 + enhance_prompt off).
import fs from "node:fs";
import path from "node:path";
import { episodePaths } from "./lib/paths.js";
import { slugArg, hasFlag } from "./lib/episode.js";
import { loadSource, clipCandidates } from "./lib/source.js";
import { generateClip, MOTION, MODELS, SAFE_DEFAULTS } from "./lib/higgsfield.js";

const slug = slugArg();
const DRY = hasFlag("dry");
const FORCE = hasFlag("force");

function opt(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : fallback;
}

const model = opt("model", SAFE_DEFAULTS.model);
if (!MODELS.includes(model)) throw new Error(`모델은 ${MODELS.join(" | ")} 중 하나 (받은 값: ${model})`);
// --strength 를 주면 전역 강제, 안 주면 역할별 기본값(ROLE.strength)을 쓴다
const strengthArg = opt("strength", null);
const strengthOf = (role) =>
  strengthArg != null ? Number(strengthArg) : (ROLE[role] ?? ROLE.detail).strength;
const only = opt("only", null);

// 이미지 역할별 카메라 문법. 상품이 변형되지 않는 선에서만 움직인다.
// strength 는 역할마다 다르다. 손·글자가 많이 걸린 컷일수록 낮춘다(변형 위험).
const ROLE = {
  hero:    { motion: MOTION.dollyIn,   strength: 0.3,  beat: "the camera pushes in slowly and steadily toward the product" },
  detail:  { motion: MOTION.dollyLeft, strength: 0.35, beat: "the camera drifts slowly sideways across the product surface" },
  scale:   { motion: MOTION.dollyOut,  strength: 0.3,  beat: "the camera pulls back slowly to reveal the product in context" },
  usage:   { motion: MOTION.static,    strength: 0.2,  beat: "the scene holds almost still, only the poured product and hand move a little" },
  package: { motion: MOTION.static,    strength: 0.2,  beat: "the camera holds nearly still with only a faint breathing drift" },
};

/** 상품이 절대 바뀌면 안 되므로 "보존" 지시를 프롬프트에 못 박는다 */
function buildPrompt(cand) {
  const r = ROLE[cand.role] ?? ROLE.detail;
  return [
    `A real product photograph of ${cand.productName} comes gently to life as live-action footage.`,
    `${r.beat}.`,
    "The product itself must stay EXACTLY as in the source image:",
    "identical shape, proportions, colour, material, markings and packaging — do not redesign, replace or restyle it.",
    "Keep the original lighting and background. Natural, subtle motion only.",
    "No text, no letters, no numbers, no logos added, no watermark, no people's faces.",
    cand.note ? `Context: ${cand.note}.` : "",
  ].filter(Boolean).join(" ");
}

const src = loadSource(slug);
const P = episodePaths(slug);
fs.mkdirSync(P.media, { recursive: true });

let log = fs.existsSync(P.clipLog) ? JSON.parse(fs.readFileSync(P.clipLog, "utf8")) : {};
let cands = clipCandidates(src);
if (only) cands = cands.filter((c) => c.key === only);
if (!cands.length) throw new Error(only ? `--only ${only} 에 해당하는 이미지 없음` : "source.json 에 images 가 없음");

console.log(`${src.type} 타입 · 상품 ${src.products.length}개 · 클립 후보 ${cands.length}개 · 모델 ${model} · strength ${strengthArg ?? "역할별"}`);

if (DRY) {
  for (const c of cands) {
    const done = log[c.key] && fs.existsSync(path.join(P.media, `${c.key}.mp4`));
    const rr = ROLE[c.role] ?? ROLE.detail;
    const mname = Object.keys(MOTION).find((k) => MOTION[k] === rr.motion);
    console.log(`  ${done && !FORCE ? "=" : "▶"} ${c.key.padEnd(14)} ${c.role.padEnd(8)} ${mname.padEnd(10)} str ${strengthOf(c.role)}  ${c.url.slice(0, 58)}`);
  }
  const todo = cands.filter((c) => FORCE || !(log[c.key] && fs.existsSync(path.join(P.media, `${c.key}.mp4`))));
  console.log(`\n생성 대상 ${todo.length}개 — 실제 크레딧 차감은 Higgsfield 콘솔에서 확인할 것 (dry-run, 아무것도 호출하지 않음)`);
  process.exit(0);
}

for (const c of cands) {
  const out = path.join(P.media, `${c.key}.mp4`);
  if (!FORCE && log[c.key] && fs.existsSync(out)) {
    console.log(`= ${c.key} 이미 있음 — 건너뜀`);
    continue;
  }
  const r = ROLE[c.role] ?? ROLE.detail;
  const prompt = buildPrompt(c);
  process.stdout.write(`▶ ${c.key} (${c.role}) 제출… `);
  const res = await generateClip(
    { imageUrl: c.url, prompt, model, motion: r.motion, strength: strengthOf(c.role), seed: log[c.key]?.seed },
    { onTick: (states, sec) => process.stdout.write(`\r▶ ${c.key} (${c.role}) ${states.join(",")} ${sec}s   `) },
  );
  const buf = Buffer.from(await (await fetch(res.url)).arrayBuffer());
  fs.writeFileSync(out, buf);
  log[c.key] = {
    productId: c.productId, role: c.role, sourceImage: c.url,
    jobSetId: res.jobSetId, seed: res.seed, model, strength: strengthOf(c.role),
    prompt, bytes: buf.length, at: new Date().toISOString(),
  };
  fs.writeFileSync(P.clipLog, JSON.stringify(log, null, 2) + "\n");
  console.log(`\r✓ ${c.key} (${c.role}) → media/${c.key}.mp4 (${Math.round(buf.length / 1024)}KB)      `);
}

console.log(`\n클립 완료. episode.json 의 씬에 연결할 것:`);
for (const c of cands) console.log(`  "${c.productId}" → onScreen.bgVideo: "media/${c.key}.mp4"`);
