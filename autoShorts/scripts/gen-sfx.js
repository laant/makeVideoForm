// assets/sfx/*.wav 를 FFmpeg 신디사이즈로 생성 (저작권 걱정 없는 기본 효과음)
//   npm run sfx [-- --force]
// 더 좋은 음원이 있으면 같은 이름의 wav 로 교체하면 된다.
import fs from "node:fs";
import path from "node:path";
import { SFX_DIR } from "./lib/paths.js";
import { run } from "./lib/proc.js";

// lavfi 필터그래프 안에서 콤마는 필터 구분자이므로 수식 내부 콤마를 이스케이프
const expr = (e) => e.replace(/,/g, "\\,");

const SFX = {
  click: [`anoisesrc=d=0.04:c=white:a=0.9`, `highpass=f=2500,afade=t=out:d=0.04`],
  pop: [`aevalsrc=${expr("sin(2*PI*(420+2600*exp(-30*t))*t)*exp(-22*t)*0.8")}:d=0.18`, `afade=t=out:st=0.12:d=0.06`],
  whoosh: [`anoisesrc=d=0.55:c=pink:a=0.9`, `bandpass=f=1400:w=1800,afade=t=in:d=0.3:curve=exp,afade=t=out:st=0.3:d=0.25`],
  chime: [`aevalsrc=${expr("(sin(2*PI*1318.5*t)+0.6*sin(2*PI*1975.5*t)*gt(t,0.09))*exp(-3.5*t)*0.35")}:d=1.1`, `afade=t=out:st=0.9:d=0.2`],
  notify: [`aevalsrc=${expr("(sin(2*PI*880*t)*lt(t,0.11)+sin(2*PI*1318.5*t)*gte(t,0.11))*exp(-5*t)*0.5")}:d=0.5`, `afade=t=out:st=0.4:d=0.1`],
  error: [`aevalsrc=${expr("sgn(sin(2*PI*160*t))*0.18*(mod(floor(t*9),2))")}:d=0.45`, `lowpass=f=2200,afade=t=out:st=0.35:d=0.1`],
  typing: [
    `aevalsrc=${expr("(random(0)*2-1)*exp(-90*mod(t+0.013*sin(t*37),0.105))*0.6")}:d=1.3`,
    `highpass=f=1200,lowpass=f=7000,afade=t=out:st=1.1:d=0.2`,
  ],
};

fs.mkdirSync(SFX_DIR, { recursive: true });
for (const [name, [src, chain]] of Object.entries(SFX)) {
  const out = path.join(SFX_DIR, `${name}.wav`);
  if (fs.existsSync(out) && !process.argv.includes("--force")) {
    console.log(`= ${name}.wav 있음`);
    continue;
  }
  await run("ffmpeg", ["-y", "-loglevel", "error", "-f", "lavfi", "-i", src, "-af", chain, "-ar", "44100", "-ac", "2", out]);
  console.log(`▶ ${name}.wav`);
}
console.log(`✓ 효과음 → ${path.relative(process.cwd(), SFX_DIR)}`);
