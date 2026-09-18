// 씬별 나레이션 생성 + 단어 타임스탬프 → episode.json timing, audio/narration.mp3
//   npm run tts -- <slug> [--mock] [--force]
//   voice.provider: "elevenlabs"(기본, 타임스탬프 포함) | "gemini"(whisper.cpp 로 단어 시간 추출)
//   --mock : TTS 대신 macOS `say`(크레딧 소모 없음, 파이프라인 테스트용)
//   --force: 캐시 무시하고 전체 재생성
import "./lib/env.js";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { loadEpisode, saveEpisode, slugArg, hasFlag } from "./lib/episode.js";
import { ROOT, episodePaths } from "./lib/paths.js";
import { run, mediaDuration, round3 } from "./lib/proc.js";
import { alignWords } from "./lib/align.js";

const slug = slugArg();
const MOCK = hasFlag("mock");
const FORCE = hasFlag("force");
const ep = loadEpisode(slug);
const P = episodePaths(slug);
fs.mkdirSync(P.audio, { recursive: true });

const PROVIDER = ep.voice.provider;
const GEMINI = PROVIDER === "gemini";
const voiceId = GEMINI
  ? ep.voice.voiceId || process.env.GEMINI_VOICE || "Aoede"
  : ep.voice.voiceId || process.env.ELEVENLABS_VOICE_ID || "";
const modelId = GEMINI
  ? ep.voice.modelId || process.env.GEMINI_TTS_MODEL || "gemini-3.1-flash-tts-preview"
  : ep.voice.modelId || process.env.ELEVENLABS_MODEL_ID || "eleven_multilingual_v2";
const WHISPER_BIN = process.env.WHISPER_BIN || "whisper-cli";
const WHISPER_MODEL = path.resolve(ROOT, process.env.WHISPER_MODEL || ".cache/whisper/ggml-small.bin");
const voiceSettings = {
  stability: ep.voice.stability,
  similarity_boost: ep.voice.similarityBoost,
  style: ep.voice.style,
  speed: ep.voice.speed,
};

if (!MOCK && GEMINI && !process.env.GEMINI_API_KEY) {
  console.error("GEMINI_API_KEY 가 없습니다. .env 를 채우거나 --mock 으로 테스트하세요.");
  process.exit(1);
}
if (!MOCK && !GEMINI && (!process.env.ELEVENLABS_API_KEY || !voiceId)) {
  console.error("ELEVENLABS_API_KEY / voiceId 가 없습니다. .env 를 채우거나 --mock 으로 테스트하세요.");
  process.exit(1);
}

function sceneHash(scene) {
  const basis = MOCK
    ? ["mock", scene.narration]
    : GEMINI
      ? ["gemini", voiceId, modelId, ep.voice.prompt, scene.narration]
      : [voiceId, modelId, JSON.stringify(voiceSettings), scene.narration];
  return crypto.createHash("sha1").update(basis.join("\n")).digest("hex").slice(0, 12);
}

/** 문자 단위 정렬 → 공백 기준 단어 */
function charsToWords(chars, starts, ends) {
  const words = [];
  let cur = null;
  chars.forEach((ch, i) => {
    if (/\s/.test(ch)) {
      if (cur) words.push(cur);
      cur = null;
      return;
    }
    if (!cur) cur = { text: "", start: starts[i], end: ends[i] };
    cur.text += ch;
    cur.end = ends[i];
  });
  if (cur) words.push(cur);
  return words.map((w) => ({ text: w.text, start: round3(w.start), end: round3(w.end) }));
}

async function elevenlabs(scene, idx, mp3Path) {
  const url = `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}/with-timestamps?output_format=mp3_44100_128`;
  const body = {
    text: scene.narration,
    model_id: modelId,
    voice_settings: voiceSettings,
    // 앞뒤 문맥을 주면 씬 단위로 끊어 생성해도 억양이 자연스럽게 이어진다
    previous_text: ep.scenes[idx - 1]?.narration,
    next_text: ep.scenes[idx + 1]?.narration,
  };
  const res = await fetch(url, {
    method: "POST",
    headers: { "xi-api-key": process.env.ELEVENLABS_API_KEY, "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`ElevenLabs ${res.status}: ${await res.text()}`);
  const data = await res.json();
  fs.writeFileSync(mp3Path, Buffer.from(data.audio_base64, "base64"));
  const a = data.alignment ?? data.normalized_alignment;
  return charsToWords(a.characters, a.character_start_times_seconds, a.character_end_times_seconds);
}

/** Gemini TTS → mp3, whisper.cpp 로 인식한 토큰 시간을 대본 단어에 정렬 */
async function gemini(scene, mp3Path) {
  const text = ep.voice.prompt ? `${ep.voice.prompt}\n\n${scene.narration}` : scene.narration;
  const body = {
    contents: [{ parts: [{ text }] }],
    generationConfig: {
      responseModalities: ["AUDIO"],
      speechConfig: { voiceConfig: { prebuiltVoiceConfig: { voiceName: voiceId } } },
    },
  };
  // 새 형식 키(AQ.…)는 x-goog-api-key 헤더를 거부하고 ?key= 만 받는다. URL 은 로그에 남기지 않음
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${modelId}:generateContent?key=${encodeURIComponent(process.env.GEMINI_API_KEY)}`;
  let data;
  for (let attempt = 1; ; attempt++) {
    const res = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    if (res.ok) {
      data = await res.json();
      break;
    }
    const msg = await res.text();
    if (attempt < 4 && (res.status === 429 || res.status >= 500)) {
      console.warn(`  Gemini ${res.status} — ${attempt * 5}s 후 재시도`);
      await new Promise((r) => setTimeout(r, attempt * 5000));
      continue;
    }
    throw new Error(`Gemini ${res.status}: ${msg.slice(0, 500)}`);
  }
  const part = data.candidates?.[0]?.content?.parts?.find((p) => p.inlineData);
  if (!part) throw new Error(`Gemini 응답에 오디오 없음: ${JSON.stringify(data).slice(0, 300)}`);
  const rate = Number(part.inlineData.mimeType.match(/rate=(\d+)/)?.[1] ?? 24000);

  const tmp = path.join(os.tmpdir(), `autoshorts-${process.pid}-${scene.id}`);
  fs.writeFileSync(`${tmp}.pcm`, Buffer.from(part.inlineData.data, "base64"));
  // 앞뒤 무음 정리(0.05s 남김) → mp3(재생용) + 16k wav(인식용)
  const trim =
    "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05," +
    "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse";
  await run("ffmpeg", ["-y", "-loglevel", "error", "-f", "s16le", "-ar", String(rate), "-ac", "1", "-i", `${tmp}.pcm`, "-af", trim, `${tmp}.wav`]);
  await run("ffmpeg", ["-y", "-loglevel", "error", "-i", `${tmp}.wav`, "-ar", "44100", "-ac", "1", "-b:a", "128k", mp3Path]);
  await run("ffmpeg", ["-y", "-loglevel", "error", "-i", `${tmp}.wav`, "-ar", "16000", "-ac", "1", `${tmp}-16k.wav`]);

  await run(WHISPER_BIN, ["-m", WHISPER_MODEL, "-l", "ko", "-f", `${tmp}-16k.wav`, "-ojf", "-of", tmp, "-np"], { capture: true });
  const out = JSON.parse(fs.readFileSync(`${tmp}.json`, "utf8"));
  const tokens = out.transcription
    .flatMap((seg) => seg.tokens)
    .filter((t) => !/^\s*\[/.test(t.text))
    .map((t) => ({ text: t.text, from: t.offsets.from / 1000, to: t.offsets.to / 1000 }));
  for (const ext of [".pcm", ".wav", "-16k.wav", ".json"]) fs.rmSync(`${tmp}${ext}`, { force: true });

  const { words, matchRatio, recognized } = alignWords(scene.narration, tokens, mediaDuration(mp3Path));
  const pct = Math.round(matchRatio * 100);
  // 일치율이 낮으면 발음이 틀렸거나, 지시문(prompt)까지 읽었거나, 싱크가 부정확할 수 있다
  if (matchRatio < 0.7) console.warn(`  ⚠ ${scene.id} 인식 일치율 ${pct}% — 들어보고 확인: "${recognized}"`);
  else console.log(`  ${scene.id} 인식 일치율 ${pct}%`);
  return { words, recognized, matchRatio: round3(matchRatio) };
}

async function ensureWhisper() {
  const probe = await run(WHISPER_BIN, ["--help"], { capture: true }).catch(() => null);
  if (!probe) throw new Error(`${WHISPER_BIN} 없음 → brew install whisper-cpp`);
  if (!fs.existsSync(WHISPER_MODEL)) {
    const name = path.basename(WHISPER_MODEL);
    console.log(`▶ whisper 모델 다운로드 (${name}, 수백 MB, 최초 1회) → ${path.relative(ROOT, WHISPER_MODEL)}`);
    fs.mkdirSync(path.dirname(WHISPER_MODEL), { recursive: true });
    await run("curl", ["-fL", "-o", `${WHISPER_MODEL}.part`, `https://huggingface.co/ggerganov/whisper.cpp/resolve/main/${name}`]);
    fs.renameSync(`${WHISPER_MODEL}.part`, WHISPER_MODEL);
  }
}

async function mockSay(scene, mp3Path) {
  const tmp = path.join(os.tmpdir(), `autoshorts-${process.pid}-${scene.id}.aiff`);
  await run("say", ["-v", process.env.MOCK_VOICE || "Yuna", "-r", "210", "-o", tmp, scene.narration]);
  // say 는 무음 없이 바로 시작 → 첫 단어 시간(0.05s)에 맞춰 앞 여백 0.05s (머리 잘림 방지)
  await run("ffmpeg", ["-y", "-loglevel", "error", "-i", tmp, "-af", "adelay=50:all=1", "-ar", "44100", "-ac", "1", "-b:a", "128k", mp3Path]);
  fs.rmSync(tmp, { force: true });
  // 글자 수 비례로 단어 시간 추정
  const dur = mediaDuration(mp3Path);
  const tokens = scene.narration.split(/\s+/).filter(Boolean);
  const total = tokens.reduce((n, t) => n + t.length, 0);
  const usable = dur - 0.1;
  let t = 0.05;
  return tokens.map((text) => {
    const len = (text.length / total) * usable;
    const w = { text, start: round3(t), end: round3(t + len * 0.92) };
    t += len;
    return w;
  });
}

let generated = 0;
let whisperReady = false;
for (const [idx, scene] of ep.scenes.entries()) {
  const hash = sceneHash(scene);
  const mp3 = path.join(P.audio, `${scene.id}.mp3`);
  const cacheJson = path.join(P.audio, `${scene.id}.json`);
  const cached = fs.existsSync(cacheJson) && JSON.parse(fs.readFileSync(cacheJson, "utf8"));
  let words;
  if (!FORCE && cached?.hash === hash && fs.existsSync(mp3)) {
    words = cached.words;
    console.log(`= ${scene.id} 캐시 사용`);
  } else {
    const label = MOCK ? "mock/say" : GEMINI ? `Gemini ${voiceId}` : "ElevenLabs";
    console.log(`▶ ${scene.id} 음성 생성 (${label}) "${scene.narration.slice(0, 30)}…"`);
    let extra = {};
    if (MOCK) words = await mockSay(scene, mp3);
    else if (GEMINI) {
      if (!whisperReady) await ensureWhisper();
      whisperReady = true;
      ({ words, ...extra } = await gemini(scene, mp3));
    } else words = await elevenlabs(scene, idx, mp3);
    fs.writeFileSync(cacheJson, JSON.stringify({ hash, words, ...extra }, null, 2));
    generated++;
  }
  scene.timing = { hash, start: 0, duration: 0, speechEnd: round3(mediaDuration(mp3)), words };
}

// 슬롯 = 발화 길이 + 여백. 전체 타임라인 기준 start 누적
let cursor = 0;
for (const scene of ep.scenes) {
  scene.timing.start = round3(cursor);
  scene.timing.duration = round3(scene.timing.speechEnd + ep.gapSeconds);
  cursor += scene.timing.duration;
}

// 씬 음성을 슬롯 길이로 패딩해 하나의 narration.mp3 로 연결 (싱크 드리프트 방지)
const inputs = ep.scenes.flatMap((s) => ["-i", path.join(P.audio, `${s.id}.mp3`)]);
const pads = ep.scenes
  .map((s, i) => `[${i}:a]aresample=44100,aformat=channel_layouts=mono,apad=whole_dur=${s.timing.duration}[a${i}]`)
  .join(";");
const concat = ep.scenes.map((_, i) => `[a${i}]`).join("") + `concat=n=${ep.scenes.length}:v=0:a=1[out]`;
await run("ffmpeg", [
  "-y", "-loglevel", "error", ...inputs,
  "-filter_complex", `${pads};${concat}`, "-map", "[out]", "-ar", "44100", "-b:a", "192k", P.narration,
]);

saveEpisode(ep);
const total = mediaDuration(P.narration);
console.log(`✓ 나레이션 ${round3(total)}s (새로 생성 ${generated}개 / 전체 ${ep.scenes.length}개) → ${path.relative(process.cwd(), P.narration)}`);
if (total > 90) console.warn("⚠ 90초 초과 — 쇼츠/릴스 길이 제한을 확인하세요.");
