// final.mp4 기술 검수 + 검수용 프레임 추출
//   npm run verify -- <slug>
import fs from "node:fs";
import path from "node:path";
import { episodePaths } from "./lib/paths.js";
import { loadEpisode, requireTiming, slugArg } from "./lib/episode.js";
import { run, ffprobeJson, mediaDuration, round3 } from "./lib/proc.js";

const slug = slugArg();
const ep = loadEpisode(slug);
requireTiming(ep);
const P = episodePaths(slug);
if (!fs.existsSync(P.final)) throw new Error(`final.mp4 없음 → npm run assemble -- ${slug}`);

const info = ffprobeJson(P.final);
const v = info.streams.find((s) => s.codec_type === "video");
const a = info.streams.find((s) => s.codec_type === "audio");
const dur = Number(info.format.duration);
const narr = mediaDuration(P.narration);
const [num, den] = v.r_frame_rate.split("/").map(Number);
const fps = num / den;
const frames = Number(v.nb_frames);

const checks = [
  ["해상도 1080x1920 (9:16)", v.width === 1080 && v.height === 1920, `${v.width}x${v.height}`],
  ["FPS 30", Math.abs(fps - 30) < 0.01, `${round3(fps)}`],
  ["코덱 H.264 / yuv420p", v.codec_name === "h264" && v.pix_fmt === "yuv420p", `${v.codec_name}/${v.pix_fmt}`],
  ["오디오 스트림 AAC", a?.codec_name === "aac", a?.codec_name ?? "없음"],
  ["길이 = 나레이션 ±0.15s", Math.abs(dur - narr) <= 0.15, `영상 ${round3(dur)}s / 음성 ${round3(narr)}s`],
  ["프레임 수 ≈ 길이×30", Math.abs(frames - dur * 30) <= 2, `${frames}f`],
  ["길이 ≤ 90s (릴스/쇼츠)", dur <= 90, `${round3(dur)}s`],
];

// 검은 화면 / 무음 구간 탐지
const { err: detect } = await run(
  "ffmpeg",
  ["-hide_banner", "-i", P.final, "-vf", "blackdetect=d=0.3:pix_th=0.05", "-af", "silencedetect=n=-45dB:d=1.2", "-f", "null", "-"],
  { capture: true },
);
const blacks = [...detect.matchAll(/black_start:([\d.]+) black_end:([\d.]+)/g)].map((m) => `${m[1]}~${m[2]}`);
const silences = [...detect.matchAll(/silence_start: ([\d.]+)/g)].map((m) => m[1]);
checks.push(["검은 화면 0.3s+ 없음", blacks.length === 0, blacks.join(", ") || "-"]);
checks.push(["1.2s+ 무음 없음", silences.length === 0, silences.join(", ") || "-"]);

// 첫/끝 프레임 + 씬별 중간 프레임
fs.rmSync(P.check, { recursive: true, force: true });
fs.mkdirSync(P.check, { recursive: true });
const grab = (t, name, extra = []) =>
  run("ffmpeg", ["-y", "-loglevel", "error", ...extra, "-ss", String(t), "-i", P.final, "-frames:v", "1", "-vf", "scale=540:-1", path.join(P.check, name)]);
await grab(0, "00-first.png");
await run("ffmpeg", ["-y", "-loglevel", "error", "-sseof", "-0.1", "-i", P.final, "-frames:v", "1", "-vf", "scale=540:-1", path.join(P.check, "zz-last.png")]);
for (const s of ep.scenes) {
  await grab(round3(s.timing.start + Math.min(s.timing.speechEnd * 0.7, s.timing.duration - 0.1)), `${s.id}-mid.png`);
}
// 한 장으로 보는 컨택트시트
const sheetInputs = fs.readdirSync(P.check).filter((f) => f.endsWith(".png")).sort();
await run("ffmpeg", [
  "-y", "-loglevel", "error",
  ...sheetInputs.flatMap((f) => ["-i", path.join(P.check, f)]),
  "-filter_complex", `${sheetInputs.map((_, i) => `[${i}:v]scale=270:480[t${i}]`).join(";")};${sheetInputs.map((_, i) => `[t${i}]`).join("")}hstack=inputs=${sheetInputs.length}`,
  path.join(P.check, "contact-sheet.jpg"),
]);

let ok = true;
for (const [name, pass, detail] of checks) {
  console.log(`${pass ? "✓" : "✗"} ${name.padEnd(24)} ${detail}`);
  ok &&= pass;
}
console.log(`\n검수 이미지: ${path.relative(process.cwd(), P.check)}/ (contact-sheet.jpg)`);
if (!ok) {
  console.error("✗ 검수 실패");
  process.exit(1);
}
console.log("✓ 검수 통과 — 업로드 전 contact-sheet 와 미리보기(npm run preview)로 최종 확인하세요.");
