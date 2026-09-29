// 배경 이미지 생성 — 씬별 onScreen.bgPrompt(피사체 한 줄) + 스타일 프리셋 → media/bg-sNN.png
//   npm run bg -- <slug> [--dry] [--force] [--only s02] [--preset clay]
//   npm run bg -- --preview [preset|all]      # 프리셋 견본 1장씩 → .cache/bg-previews/
//
// 프롬프트 = style + SUBJECT + layout + accent + prohibit (templates/bg-presets.json).
// style·layout·prohibit 가 에피소드 안에서 고정되므로 씬마다 피사체만 바뀌고 분위기는 통일된다.
// 생성은 OpenMontage 의 GoogleImagen(gemini-3.1-flash-image)을 쓴다 — scripts/lib/imagen.py.
// 유료 호출이라 make 에는 넣지 않는다. 이미 있는 파일은 건너뛴다(--force 로 재생성).
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { ROOT, TEMPLATES, episodePaths } from "./lib/paths.js";
import { loadEpisode, saveEpisode, hasFlag } from "./lib/episode.js";

const PRESETS = JSON.parse(fs.readFileSync(path.join(TEMPLATES, "bg-presets.json"), "utf8"));
const presetNames = Object.keys(PRESETS).filter((k) => !k.startsWith("_"));
const OM = process.env.OPENMONTAGE_DIR || path.resolve(ROOT, "../OpenMontage");
const PY = path.join(OM, ".venv/bin/python");

function opt(name) {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 && process.argv[i + 1] && !process.argv[i + 1].startsWith("--") ? process.argv[i + 1] : null;
}

/** #RRGGBB → 프롬프트용 색 이름 (theme.accent 에서 림라이트 색을 자동으로 뽑는다) */
export function accentName(hex) {
  const m = /^#?([0-9a-f]{6})$/i.exec(hex || "");
  if (!m) return "soft neutral silver";
  const n = parseInt(m[1], 16), r = (n >> 16) / 255, g = ((n >> 8) & 255) / 255, b = (n & 255) / 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b), d = max - min;
  if (d < 0.12) return "soft neutral silver";
  let h = max === r ? ((g - b) / d) % 6 : max === g ? (b - r) / d + 2 : (r - g) / d + 4;
  h = (h * 60 + 360) % 360;
  if (h < 15 || h >= 340) return "soft warm red";
  if (h < 45) return "warm amber";
  if (h < 65) return "soft golden yellow";
  if (h < 140) return "soft green";
  if (h < 170) return "soft mint-green";
  if (h < 200) return "soft teal";
  if (h < 250) return "cool blue";
  if (h < 290) return "soft violet";
  return "soft pink";
}

export function buildPrompt(preset, subject, { layout = "plate", accent }) {
  const P = PRESETS[preset];
  if (!P) throw new Error(`프리셋 없음: ${preset} (있는 것: ${presetNames.join(", ")})`);
  const L = PRESETS._layouts[layout];
  if (!L) throw new Error(`layout 은 ${Object.keys(PRESETS._layouts).join(" | ")}`);
  return [P.style, `SUBJECT: ${subject.replace(/\.$/, "")}.`, L,
          (P.accent || PRESETS._accent).replace("{accent}", accent), PRESETS._prohibit].join(" ");
}

function generate(jobs) {
  if (!fs.existsSync(PY)) throw new Error(`OpenMontage venv 없음: ${PY} (OPENMONTAGE_DIR 로 지정 가능)`);
  const r = spawnSync(PY, [path.join(ROOT, "scripts/lib/imagen.py")], {
    input: JSON.stringify(jobs), encoding: "utf8", maxBuffer: 64 * 1024 * 1024,
  });
  const results = (r.stdout || "").split("\n").filter((l) => l.startsWith("@@RESULT "))
    .map((l) => JSON.parse(l.slice(9)));
  if (r.status !== 0 && !results.length) throw new Error(`이미지 생성 실패:\n${(r.stderr || "").slice(-1500)}`);
  return results;
}

// ── 프리셋 견본 ─────────────────────────────────────────────
if (hasFlag("preview")) {
  const which = opt("preview") || "all";
  const names = which === "all" ? presetNames : [which];
  // 재질 중립 문장이어야 한다 — 피사체에 "clay" 같은 재질을 쓰면 프리셋 스타일을 이긴다
  const SUBJECT = "a small plain smartphone lying face up on the floor next to a single round coin";
  const dir = path.join(ROOT, ".cache/bg-previews");
  const jobs = names.map((n) => ({ prompt: buildPrompt(n, SUBJECT, { accent: "warm amber" }),
                                   out: path.join(dir, `${n}.png`) }))
    .filter((j) => hasFlag("force") || !fs.existsSync(j.out));
  if (jobs.length) for (const res of generate(jobs)) console.log(`${res.ok ? "✓" : "✗"} ${path.basename(res.out)} ${res.error || ""}`);
  for (const n of names) console.log(`  ${n.padEnd(10)} ${PRESETS[n].label}  [${PRESETS[n].verified}]  → .cache/bg-previews/${n}.png`);
  process.exit(0);
}

// ── 에피소드 ─────────────────────────────────────────────────
const slug = process.argv.slice(2).find((a, i, all) => !a.startsWith("-") && !["preset", "only"].includes(all[i - 1]?.replace(/^--/, "")));
if (!slug) { console.error("사용법: npm run bg -- <slug> [--dry] [--force] [--only sNN] [--preset 이름]\n       npm run bg -- --preview [all|프리셋]"); process.exit(1); }
const ep = loadEpisode(slug);
const P = episodePaths(slug);
const preset = opt("preset") || ep.bg.preset;
const layout = ep.bg.layout;
const accent = ep.bg.accent || accentName(ep.theme.accent);
const only = opt("only");
const DRY = hasFlag("dry"), FORCE = hasFlag("force");

console.log(`프리셋 ${preset} (${PRESETS[preset]?.label}) · layout ${layout} · 림라이트 "${accent}"`);
const targets = ep.scenes.filter((s) => s.onScreen.bgPrompt && (!only || s.id === only));
const noPrompt = ep.scenes.filter((s) => !s.onScreen.bgPrompt && !s.onScreen.bgImage).map((s) => s.id);
if (noPrompt.length) console.log(`  bgPrompt 없음(배경 없이 렌더): ${noPrompt.join(", ")}`);
if (!targets.length) { console.log("생성할 씬이 없다 — 씬의 onScreen.bgPrompt 에 피사체 한 줄을 적을 것"); process.exit(0); }

const jobs = [];
for (const s of targets) {
  const rel = `media/bg-${s.id}.png`, out = path.join(P.dir, rel);
  const prompt = buildPrompt(preset, s.onScreen.bgPrompt, { layout, accent });
  const skip = fs.existsSync(out) && !FORCE;
  console.log(`  ${skip ? "=" : "▶"} ${s.id}  ${s.onScreen.bgPrompt.slice(0, 80)}`);
  if (DRY && hasFlag("verbose")) console.log(`      ${prompt}`);
  if (!skip) jobs.push({ id: s.id, rel, out, prompt });
}
if (DRY) { console.log(`\n생성 대상 ${jobs.length}장 (dry-run — 호출 없음)`); process.exit(0); }

const results = jobs.length ? generate(jobs.map(({ prompt, out }) => ({ prompt, out }))) : [];
const manPath = path.join(P.refs, "bg_manifest.json");
const man = fs.existsSync(manPath) ? JSON.parse(fs.readFileSync(manPath, "utf8")) : { assets: [] };
let failed = 0;
for (const j of jobs) {
  const res = results.find((x) => x.out === j.out);
  if (!res?.ok) { failed++; console.log(`✗ ${j.id} ${res?.error || "결과 없음"}`); continue; }
  console.log(`✓ ${j.id} → ${j.rel}`);
  man.assets = man.assets.filter((a) => a.file !== j.rel);
  man.assets.push({ file: j.rel, scene: j.id, preset, layout, tool: "google_imagen", model: res.model,
                    prompt: j.prompt, at: new Date().toISOString() });
}
// 씬에 배경 연결 (이미 다른 배경이 지정돼 있으면 건드리지 않는다)
for (const s of targets) {
  const rel = `media/bg-${s.id}.png`;
  if (!fs.existsSync(path.join(P.dir, rel))) continue;
  if (!s.onScreen.bgImage) s.onScreen.bgImage = rel;
  if (s.onScreen.bgDim == null) s.onScreen.bgDim = PRESETS[preset].dim;
}
fs.mkdirSync(P.refs, { recursive: true });
fs.writeFileSync(manPath, JSON.stringify(man, null, 1) + "\n");
saveEpisode(ep);
console.log(`\n${jobs.length - failed}장 생성 · ${failed}장 실패 → npm run scenes -- ${slug}`);
if (failed) process.exit(1);
