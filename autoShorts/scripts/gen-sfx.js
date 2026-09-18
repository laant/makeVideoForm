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
  click: [`anoisesrc=d=0.04:c=white:a=0.9:seed=42`, `highpass=f=2500,afade=t=out:d=0.04`],
  pop: [`aevalsrc=${expr("sin(2*PI*(420+2600*exp(-30*t))*t)*exp(-22*t)*0.8")}:d=0.18`, `afade=t=out:st=0.12:d=0.06`],
  whoosh: [`anoisesrc=d=0.55:c=pink:a=0.9:seed=42`, `bandpass=f=1400:width_type=h:w=1800,afade=t=in:d=0.3:curve=exp,afade=t=out:st=0.3:d=0.25`],
  chime: [`aevalsrc=${expr("(sin(2*PI*1318.5*t)+0.6*sin(2*PI*1975.5*t)*gt(t,0.09))*exp(-3.5*t)*0.35")}:d=1.1`, `afade=t=out:st=0.9:d=0.2`],
  notify: [`aevalsrc=${expr("(sin(2*PI*880*t)*lt(t,0.11)+sin(2*PI*1318.5*t)*gte(t,0.11))*exp(-5*t)*0.5")}:d=0.5`, `afade=t=out:st=0.4:d=0.1`],
  error: [`aevalsrc=${expr("sgn(sin(2*PI*160*t))*0.18*(mod(floor(t*9),2))")}:d=0.45`, `lowpass=f=2200,afade=t=out:st=0.35:d=0.1`],
  typing: [
    `aevalsrc=${expr("(random(0)*2-1)*exp(-90*mod(t+0.013*sin(t*37),0.105))*0.6")}:d=1.3`,
    `highpass=f=1200,lowpass=f=7000,afade=t=out:st=1.1:d=0.2`,
  ],
  // ── 가이드 17종 확장 ──
  key: [`aevalsrc=${expr("(random(0)*2-1)*exp(-120*t)*0.7+sin(2*PI*3200*t)*exp(-200*t)*0.25")}:d=0.09`, `highpass=f=900,afade=t=out:st=0.06:d=0.03`],
  "whoosh-long": [`anoisesrc=d=1.3:c=pink:a=0.9:seed=42`, `bandpass=f=900:width_type=h:w=1400,afade=t=in:d=0.8:curve=exp,afade=t=out:st=0.8:d=0.5`],
  impact: [
    `aevalsrc=${expr("(sin(2*PI*(55+140*exp(-18*t))*t)*0.9+(random(1)*2-1)*exp(-40*t)*0.4)*exp(-5*t)")}:d=0.9`,
    `lowpass=f=1800,afade=t=out:st=0.7:d=0.2`,
  ],
  "impact-deep": [`aevalsrc=${expr("sin(2*PI*(38+90*exp(-10*t))*t)*exp(-2.6*t)*0.95")}:d=1.6`, `lowpass=f=600,afade=t=out:st=1.3:d=0.3`],
  tone: [`aevalsrc=${expr("sin(2*PI*2093*t)*exp(-4*t)*0.35")}:d=0.7`, `afade=t=in:d=0.01,afade=t=out:st=0.55:d=0.15`],
  ping: [`aevalsrc=${expr("(sin(2*PI*1760*t)+0.3*sin(2*PI*3520*t))*exp(-9*t)*0.4")}:d=0.45`, `afade=t=out:st=0.35:d=0.1`],
  sparkle: [
    `aevalsrc=${expr("(sin(2*PI*2637*t)*gte(t,0)+sin(2*PI*3136*t)*gte(t,0.07)+sin(2*PI*3951*t)*gte(t,0.14)+sin(2*PI*5274*t)*gte(t,0.21))*exp(-6*t)*0.18")}:d=0.8`,
    `afade=t=out:st=0.6:d=0.2`,
  ],
  glitch: [`aevalsrc=${expr("sgn(sin(2*PI*(300+900*random(2))*t))*lt(mod(t,0.06),0.035)*0.22")}:d=0.35`, `highpass=f=300,afade=t=out:st=0.28:d=0.07`],
  "glitch-2": [`aevalsrc=${expr("(random(3)*2-1)*lt(mod(t*37,1),0.5)*0.35")}:d=0.4`, `bandpass=f=2500:width_type=h:w=3000,afade=t=out:st=0.32:d=0.08`],
  "glitch-3": [`aevalsrc=${expr("sin(2*PI*(1200-2600*t)*t)*sgn(sin(2*PI*45*t))*0.25")}:d=0.5`, `afade=t=out:st=0.4:d=0.1`],
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
