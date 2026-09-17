// renders/sNN.mp4 + audio/narration.mp3 + SFX → final.mp4 (1080x1920, 30fps, H.264/AAC)
//   npm run assemble -- <slug>
import fs from "node:fs";
import path from "node:path";
import { SFX_DIR, episodePaths } from "./lib/paths.js";
import { loadEpisode, requireTiming, slugArg } from "./lib/episode.js";
import { run, mediaDuration, round3 } from "./lib/proc.js";

const slug = slugArg();
const ep = loadEpisode(slug);
requireTiming(ep);
const P = episodePaths(slug);

const XFADE = { crossfade: "fade", "white-flash": "fadewhite", zoom: "zoomin" };
const T = ep.transitionSeconds;

const inputs = [];
const filters = [];

// 1) 영상: 씬마다 포맷 정규화 후 xfade/concat 체인
ep.scenes.forEach((s, i) => {
  const f = path.join(P.renders, `${s.id}.mp4`);
  if (!fs.existsSync(f)) throw new Error(`${f} 없음 → npm run render -- ${slug}`);
  inputs.push("-i", f);
  filters.push(`[${i}:v]fps=30,scale=1080:1920:flags=lanczos,setsar=1,format=yuv420p,settb=AVTB[v${i}]`);
});
let acc = "v0";
let elapsed = 0; // acc 의 "슬롯 기준" 길이
ep.scenes.slice(0, -1).forEach((s, i) => {
  elapsed += s.timing.duration;
  const out = `x${i + 1}`;
  if (s.transitionOut === "cut" || T === 0) {
    filters.push(`[${acc}][v${i + 1}]concat=n=2:v=1:a=0[${out}]`);
  } else {
    filters.push(`[${acc}][v${i + 1}]xfade=transition=${XFADE[s.transitionOut]}:duration=${T}:offset=${round3(elapsed)}[${out}]`);
  }
  acc = out;
});
const total = round3(ep.scenes.reduce((n, s) => n + s.timing.duration, 0));
filters.push(`[${acc}]trim=duration=${total},setpts=PTS-STARTPTS[vout]`);

// 2) 오디오: 나레이션 + 효과음(adelay)
const nIdx = ep.scenes.length;
inputs.push("-i", P.narration);
const mix = [`[${nIdx}:a]aresample=44100,aformat=channel_layouts=stereo[narr]`];
let k = 0;
for (const s of ep.scenes) {
  for (const fx of s.sfx) {
    const file = path.join(SFX_DIR, `${fx.name}.wav`);
    if (!fs.existsSync(file)) throw new Error(`${file} 없음 → npm run sfx`);
    const local = sfxTime(s, fx.at);
    const at = Math.max(0, Math.round((s.timing.start + local) * 1000));
    inputs.push("-i", file);
    const idx = nIdx + 1 + k;
    // 나레이션 대비 약 -12dB
    mix.push(`[${idx}:a]aresample=44100,aformat=channel_layouts=stereo,volume=${0.25 * fx.volume},adelay=${at}|${at}[fx${k}]`);
    k++;
  }
}
const mixInputs = ["[narr]", ...Array.from({ length: k }, (_, i) => `[fx${i}]`)].join("");
mix.push(`${mixInputs}amix=inputs=${k + 1}:duration=first:normalize=0,alimiter=limit=0.95,atrim=duration=${total}[aout]`);

function sfxTime(scene, at) {
  if (typeof at === "number") return at;
  if (at === "start") return 0;
  if (at === "end") return scene.timing.speechEnd;
  const key = String(at).replace(/^word:/, "");
  const w = scene.timing.words.find((w) => w.text.includes(key));
  if (!w) console.warn(`⚠ ${scene.id} sfx 위치 "${at}" 단어를 못 찾아 씬 시작으로 대체`);
  return w ? w.start : 0;
}

console.log(`▶ 합성: 씬 ${ep.scenes.length}개, 효과음 ${k}개, ${total}s`);
await run("ffmpeg", [
  "-y", "-loglevel", "error", ...inputs,
  "-filter_complex", [...filters, ...mix].join(";"),
  "-map", "[vout]", "-map", "[aout]",
  "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", "30",
  "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
  "-movflags", "+faststart", P.final,
]);
console.log(`✓ ${path.relative(process.cwd(), P.final)} (${round3(mediaDuration(P.final))}s)`);
