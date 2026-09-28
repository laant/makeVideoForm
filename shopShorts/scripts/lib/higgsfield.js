// Higgsfield Cloud API — image-to-video 클라이언트.
//
// ⚠️ OpenMontage 의 tools/video/higgsfield_video.py 는 이 API 와 맞지 않는다(2026-09-21 실측).
//    잘못된 것: Authorization: Bearer + X-API-Secret / POST /v1/generations /
//               모델 seedance_2.0·kling_3.0·veo_3.1·sora_2 / 최상위 prompt·model·task
//    실제: 아래 그대로. text-to-video 는 존재하지 않고 image2video 만 있다.
//
// 핵심 제약: input_images 는 **공개 URL 만** 받는다.
//   - base64 불가(type 은 "image_url" 리터럴 하나뿐), 업로드 엔드포인트 없음,
//     data URI 는 2083자 제한에 걸림.
//   - 쇼핑 쇼츠에서는 상품 페이지 이미지가 이미 공개 URL 이라 그대로 넘기면 된다.
import "./env.js";

function env(name) {
  const v = process.env[name];
  if (!v) throw new Error(`${name} 없음 — shopShorts/.env 를 확인할 것`);
  return v;
}

const BASE = process.env.HIGGSFIELD_API_BASE_URL || "https://platform.higgsfield.ai";

export const MODELS = ["dop-lite", "dop-turbo", "dop-preview"];

// GET /v1/motions 의 121종 중 상품 촬영에 쓸 만한 것만. strength 를 낮게 쓰는 게 핵심.
export const MOTION = {
  static: "fa3ddb7c-53ee-4383-aa17-97ae65f180e5",
  dollyIn: "81ca2cd2-05db-4222-9ba0-a32e5185adfb",
  dollyOut: "12ac8798-5370-4801-91a6-f1acb425fc4a",
  dollyLeft: "71f0f8bc-0e5d-4d32-b34f-bd74a5e3cba8",
  dollyRight: "15ddc007-4723-42c1-8446-2af69af4879f",
  craneUp: "68af9add-43ea-4261-a706-16b640fdcff9",
  craneDown: "b26dcbe5-e784-4893-b8a3-2bd4f848e90a",
  zoomIn: "fbcbec5b-30f8-4b17-ba6e-8e8d5b265562",
  general: "31177282-bde3-4870-b283-1135ca0a201a",
};

/**
 * 상품 원형 보존 기본값.
 * 2026-09-21 04 프로젝트 실측: motions strength 1.0 + enhance_prompt=true 가 자동 적용되면
 * 5초 클립의 뒤 1/3에서 피사체가 다른 물건으로 변형됐다. 쇼핑은 상품이 변하면 못 쓰므로
 * strength 를 낮게, enhance_prompt 를 끄고, 길이를 짧게 가져간다.
 */
export const SAFE_DEFAULTS = {
  model: "dop-lite",
  motion: MOTION.dollyIn,
  strength: 0.35,
  enhancePrompt: false,
};

function headers() {
  const key = env("HIGGSFIELD_API_KEY");
  const secret = env("HIGGSFIELD_API_SECRET");
  return { "hf-api-key": key, "hf-secret": secret, "Content-Type": "application/json" };
}

async function hf(path, init = {}) {
  const res = await fetch(BASE + path, { ...init, headers: headers() });
  const text = await res.text();
  let body;
  try { body = JSON.parse(text); } catch { body = text; }
  if (!res.ok) {
    const detail = typeof body === "string" ? body : JSON.stringify(body.detail ?? body);
    throw new Error(`Higgsfield ${res.status} ${path}: ${detail}`);
  }
  return body;
}

/** 카메라 모션 프리셋 전체 목록 (id·name·description) */
export async function listMotions() {
  return hf("/v1/motions", { method: "GET" });
}

/**
 * image-to-video 제출. 반환: job set (id, jobs[])
 * @param {{imageUrl: string, prompt: string, model?: string, motion?: string,
 *          strength?: number, seed?: number, enhancePrompt?: boolean}} o
 */
export async function submitImage2Video(o) {
  if (!o.imageUrl) throw new Error("imageUrl 필요 — Higgsfield 는 공개 URL 만 받는다");
  if (/^data:/i.test(o.imageUrl)) throw new Error("data URI 불가 (2083자 제한) — 공개 URL 을 쓸 것");
  const params = {
    model: o.model ?? SAFE_DEFAULTS.model,
    prompt: o.prompt,
    input_images: [{ type: "image_url", image_url: o.imageUrl }],
    motions: [{ id: o.motion ?? SAFE_DEFAULTS.motion, strength: o.strength ?? SAFE_DEFAULTS.strength }],
    enhance_prompt: o.enhancePrompt ?? SAFE_DEFAULTS.enhancePrompt,
  };
  if (o.seed != null) params.seed = o.seed;
  return hf("/v1/image2video", { method: "POST", body: JSON.stringify({ params }) });
}

const DONE = new Set(["completed", "failed", "nsfw", "canceled", "cancelled"]);

/** job set 완료까지 폴링. 반환: 완료된 job set */
export async function waitForJobSet(id, { intervalMs = 5000, timeoutMs = 600000, onTick } = {}) {
  const started = Date.now();
  for (;;) {
    const d = await hf(`/v1/job-sets/${id}`, { method: "GET" });
    const states = d.jobs.map((j) => j.status);
    onTick?.(states, Math.round((Date.now() - started) / 1000));
    if (states.every((s) => DONE.has(s))) {
      const bad = d.jobs.filter((j) => j.status !== "completed");
      if (bad.length) throw new Error(`Higgsfield 생성 실패: ${bad.map((j) => j.status).join(", ")}`);
      return d;
    }
    if (Date.now() - started > timeoutMs) throw new Error(`Higgsfield 폴링 타임아웃 (${id})`);
    await new Promise((r) => setTimeout(r, intervalMs));
  }
}

/** 완료된 job set → 원본 mp4 URL */
export function videoUrlOf(jobSet, { quality = "raw" } = {}) {
  const r = jobSet.jobs[0]?.results;
  const url = r?.[quality]?.url ?? r?.raw?.url ?? r?.min?.url;
  if (!url) throw new Error("Higgsfield 결과에 video URL 없음");
  return url;
}

/** 제출 → 폴링 → mp4 URL 까지 한 번에 */
export async function generateClip(o, { onTick } = {}) {
  const set = await submitImage2Video(o);
  const done = await waitForJobSet(set.id, { onTick });
  return { jobSetId: set.id, url: videoUrlOf(done), seed: done.input_params?.seed };
}
