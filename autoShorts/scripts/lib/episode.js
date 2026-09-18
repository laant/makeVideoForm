import fs from "node:fs";
import { z } from "zod";
import { episodePaths } from "./paths.js";

export const TEMPLATE_NAMES = ["title", "compare", "list", "demo", "cta"];
import { TRANSITIONS, EFFECTS } from "./fx.js";
export { TRANSITIONS, EFFECTS };
// assets/sfx/<name>.wav — scripts/gen-sfx.js 가 생성 (가이드 17종)
export const SFX_NAMES = [
  "click", "key", "typing", "whoosh", "whoosh-long", "impact", "impact-deep", "tone", "pop", "ping",
  "notify", "chime", "sparkle", "error", "glitch", "glitch-2", "glitch-3",
];

const Word = z.object({ text: z.string(), start: z.number(), end: z.number() });

const Timing = z.object({
  hash: z.string(),
  start: z.number(), // 전체 영상 기준 씬 시작(초)
  duration: z.number(), // 씬 슬롯 길이(음성 + 여백)
  speechEnd: z.number(), // 씬 기준 발화 종료(초)
  words: z.array(Word), // 씬 기준 단어 타임스탬프
});

const Scene = z.object({
  id: z.string().regex(/^s\d{2}$/, "씬 id는 s01, s02 … 형식"),
  template: z.enum(TEMPLATE_NAMES),
  narration: z.string().min(1),
  // 템플릿별 화면 데이터. templates/scenes/README.md 참고
  onScreen: z.record(z.string(), z.any()).default({}),
  sfx: z
    .array(
      z.object({
        name: z.enum(SFX_NAMES),
        // "start" | "end" | 씬 기준 초 | 나레이션 속 단어("word:비교")
        at: z.union([z.number(), z.string()]).default("start"),
        volume: z.number().min(0).max(2).default(1),
      }),
    )
    .default([]),
  transitionOut: z.enum(TRANSITIONS).default("crossfade"),
  // 씬 전체에 거는 화면 효과 (합성 단계 FFmpeg, 순서대로 적용). templates/scenes/README.md
  effects: z.array(z.enum(EFFECTS)).default([]),
  timing: Timing.optional(),
});

export const EpisodeSchema = z.object({
  slug: z.string().regex(/^[a-z0-9-]+$/),
  topic: z.string(),
  audience: z.string().default(""),
  tone: z.string().default(""),
  cta: z.string().default(""),
  reference: z
    .object({
      url: z.string().default(""),
      reaction: z.string().default(""), // 조회수/반응
      transcript: z.string().default(""), // 자막·나레이션 전사
      sceneFlow: z.string().default(""), // 장면 흐름 메모(초 단위)
      notes: z.string().default(""), // /shorts-ref 분석 요약
    })
    .prefault({}),
  // 입력 페이지(npm run intake)에서 사람이 미리 적어 두는 제작 의도. Claude 는 묻기 전에 여기부터 읽는다
  brief: z
    .object({
      goal: z.string().default(""), // 시청자가 얻어갈 한 가지
      hook: z.string().default(""),
      lengthSec: z.number().min(10).max(90).default(35),
      mustShow: z.string().default(""),
      avoid: z.string().default(""),
      draft: z.string().default(""), // 내 대본 초안 (한 줄 = 한 씬: 나레이션 | 화면)
      visual: z.string().default(""), // 화면 스타일 요청
      files: z
        .array(
          z.object({
            path: z.string(), // 에피소드 폴더 기준 refs/… | media/…
            use: z.enum(["reference", "asset"]),
            note: z.string().default(""),
          }),
        )
        .default([]),
      submittedAt: z.string().default(""),
    })
    .prefault({}),
  theme: z
    .object({
      bg: z.string().default("#0b0b0f"),
      fg: z.string().default("#f5f5f7"),
      accent: z.string().default("#ffd84d"),
      muted: z.string().default("#8a8a96"),
    })
    .default({ bg: "#0b0b0f", fg: "#f5f5f7", accent: "#ffd84d", muted: "#8a8a96" }),
  voice: z
    .object({
      // elevenlabs: 단어 타임스탬프를 API 가 돌려줌 / gemini: whisper 로 시간 추출 (brew install whisper-cpp)
      provider: z.enum(["elevenlabs", "gemini"]).default("elevenlabs"),
      voiceId: z.string().default(""), // elevenlabs voice_id | gemini 보이스 이름(예: Aoede)
      prompt: z.string().default(""), // gemini 전용: 말투·속도 지시문
      modelId: z.string().default(""),
      stability: z.number().default(0.45),
      similarityBoost: z.number().default(0.8),
      style: z.number().default(0.15),
      speed: z.number().default(1.05),
    })
    .prefault({}),
  gapSeconds: z.number().min(0).default(0.25), // 씬 사이 무음 여백
  transitionSeconds: z.number().min(0).max(1).default(0.3),
  scenes: z.array(Scene).min(1),
  // 인스타 카드뉴스(1:1). onScreen.card=false 로 씬 제외, onScreen.cardNote 로 카드 전용 보충 문구
  cards: z
    .object({
      footer: z.string().default(""), // 모든 카드 하단 (출처·기준일 등)
    })
    .prefault({}),
  caption: z.string().default(""),
  hashtags: z.array(z.string()).default([]),
  upload: z
    .object({
      title: z.string().default(""),
      instagram: z.boolean().default(true),
      youtube: z.boolean().default(true),
    })
    .default({ title: "", instagram: true, youtube: true }),
});

export function slugArg() {
  const slug = process.argv.slice(2).find((a) => !a.startsWith("-"));
  if (!slug) {
    console.error("사용법: npm run <script> -- <slug> [옵션]");
    process.exit(1);
  }
  return slug;
}

export function hasFlag(name) {
  return process.argv.includes(`--${name}`);
}

export function loadEpisode(slug) {
  const p = episodePaths(slug);
  if (!fs.existsSync(p.json)) throw new Error(`episode.json 없음: ${p.json}`);
  const raw = JSON.parse(fs.readFileSync(p.json, "utf8"));
  const parsed = EpisodeSchema.safeParse(raw);
  if (!parsed.success) {
    const msg = parsed.error.issues.map((i) => `  - ${i.path.join(".")}: ${i.message}`).join("\n");
    throw new Error(`episode.json 스키마 오류:\n${msg}`);
  }
  const ids = parsed.data.scenes.map((s) => s.id);
  if (new Set(ids).size !== ids.length) throw new Error("씬 id 중복");
  return parsed.data;
}

export function saveEpisode(ep) {
  fs.writeFileSync(episodePaths(ep.slug).json, JSON.stringify(ep, null, 2) + "\n");
}

export function requireTiming(ep) {
  const missing = ep.scenes.filter((s) => !s.timing).map((s) => s.id);
  if (missing.length) throw new Error(`timing 없음(${missing.join(", ")}) → 먼저 npm run tts -- ${ep.slug}`);
}

/** 마지막 씬이 아니고 트랜지션이 cut 이 아니면, xfade 겹침만큼 꼬리를 더 렌더한다 */
export function renderDurationOf(ep, i) {
  const s = ep.scenes[i];
  const tail = i < ep.scenes.length - 1 && s.transitionOut !== "cut" ? ep.transitionSeconds : 0;
  return Math.round((s.timing.duration + tail) * 1000) / 1000;
}
