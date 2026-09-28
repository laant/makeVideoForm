import fs from "node:fs";
import { z } from "zod";
import { episodePaths } from "./paths.js";

// 쇼핑 쇼츠 전용 씬 템플릿 (autoShorts 의 title/compare/list/demo/cta 와 다르다)
export const TEMPLATE_NAMES = ["hook", "product", "spec", "compare", "verdict", "cta-link"];
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
  // 이 씬이 다루는 상품 (source.json 의 products[].id). 오버레이가 가격·스펙을 여기서 끌어온다
  productId: z.string().regex(/^p\d{2}$/).optional(),
  // 템플릿별 화면 데이터. templates/scenes/README.md 참고
  //   공통: bgVideo(media/…mp4, Higgsfield 클립) | bgImage(media/…png) | bgDim | highlight | showCaptions
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
  theme: z
    .object({
      bg: z.string().default("#0b0b0f"),
      fg: z.string().default("#f5f5f7"),
      accent: z.string().default("#ffd84d"),
      muted: z.string().default("#cfd0d8"), // 영상 배경 위 보조 텍스트 — 어두우면 묻힌다
    })
    .default({ bg: "#0b0b0f", fg: "#f5f5f7", accent: "#ffd84d", muted: "#cfd0d8" }),
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
  // a: 제휴 리뷰형 | b: 정보형 큐레이션 | c: 단일 상품 홍보
  shopType: z.enum(["a", "b", "c"]),
  /**
   * 상단 고정 헤더 (3층 구조의 1층). 전 씬에 같은 내용이 박힌다.
   * 스크롤하다 중간에 들어온 시청자도 주제를 바로 알게 하는 장치 —
   * 화장품/생활용품 쇼츠 상위권의 공통 포맷(2026-09-22 레퍼런스 분석).
   * title 을 비우면 헤더 자체를 렌더하지 않는다.
   */
  header: z
    .object({
      kicker: z.string().default(""), // 채널·시리즈 라인 (작게)
      title: z.string().default(""), // 굵은 제목. 줄바꿈 \n
      badge: z.string().default(""), // 권위 배지 (예: 식약처 기능성)
    })
    .prefault({}),
  /**
   * 고지 — 비우면 verify 가 실패한다. 영상 내 상시 배너 + caption 프리픽스로 자동 삽입된다.
   * 실사용하지 않은 체험을 후기처럼 말하지 않기 위한 장치이기도 하다(나레이션 금지어는 CLAUDE.md).
   */
  disclosure: z
    .object({
      affiliate: z.string().default(""), // 제휴/유료 광고 표시 — 리워드 링크가 있으면 필수
      aiGenerated: z.string().default(""), // AI 생성 영상 표시 — 클립을 쓰면 필수
      source: z.string().default(""), // "가격·스펙은 YYYY-MM-DD 기준" — 항상 필수
      banner: z.string().default(""), // 영상 배너에 실제로 찍히는 한 줄 (비우면 자동 조합)
    })
    .prefault({}),
  // 설명란에 넣을 링크 (리워드 링크 포함). precheck 가 실제 응답을 확인한다
  links: z.array(z.object({ label: z.string(), url: z.string() })).default([]),
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

/**
 * 영상에 상시로 찍히는 고지 한 줄. disclosure.banner 를 적었으면 그대로,
 * 안 적었으면 affiliate·aiGenerated·source 를 가운뎃점으로 조합한다.
 */
export function disclosureBanner(ep) {
  const d = ep.disclosure ?? {};
  if (d.banner) return d.banner;
  return [d.affiliate, d.aiGenerated, d.source].filter(Boolean).join(" · ");
}

/** 고지 누락 목록 — verify 와 build-scenes 가 함께 쓴다 */
export function missingDisclosure(ep) {
  const d = ep.disclosure ?? {};
  const miss = [];
  const hasReward = (ep.links ?? []).length > 0 || ep.shopType === "a" || ep.shopType === "c";
  if (hasReward && !d.affiliate) miss.push("disclosure.affiliate (제휴 링크가 있으면 필수)");
  const usesClip = ep.scenes.some((s) => s.onScreen?.bgVideo);
  if (usesClip && !d.aiGenerated) miss.push("disclosure.aiGenerated (AI 생성 클립을 쓰면 필수)");
  if (!d.source) miss.push("disclosure.source (가격·스펙 기준일은 항상 필수)");
  if (!disclosureBanner(ep)) miss.push("disclosure 배너가 비어 있음");
  return miss;
}
