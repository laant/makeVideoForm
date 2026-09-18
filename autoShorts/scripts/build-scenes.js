// episode.json + templates/scenes → episodes/<slug>/scenes/sNN.html (+ 미리보기용 index.html)
//   npm run scenes -- <slug> [--force]
// 생성 파일 첫 주석이 "autoshorts:generated" 이면 데이터/템플릿 변경 시 자동 갱신.
// Claude/사람이 직접 연출을 고친 씬은 주석을 "autoshorts:custom" 으로 바꾸면 덮어쓰지 않는다. (--force 는 무시하고 덮어씀)
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { ROOT, TEMPLATES, episodePaths } from "./lib/paths.js";
import { loadEpisode, requireTiming, renderDurationOf, slugArg, hasFlag } from "./lib/episode.js";
import { round3 } from "./lib/proc.js";

const slug = slugArg();
const FORCE = hasFlag("force");
const ep = loadEpisode(slug);
requireTiming(ep);
const P = episodePaths(slug);
fs.mkdirSync(P.scenes, { recursive: true });
fs.mkdirSync(P.vendor, { recursive: true });
fs.copyFileSync(path.join(ROOT, "node_modules/gsap/dist/gsap.min.js"), path.join(P.vendor, "gsap.min.js"));

// HyperFrames 프로젝트 메타 (에피소드 폴더 = HyperFrames 프로젝트)
fs.writeFileSync(
  path.join(P.dir, "hyperframes.json"),
  JSON.stringify({ $schema: "https://hyperframes.heygen.com/schema/hyperframes.json", paths: { assets: "audio" } }, null, 2) + "\n",
);
fs.writeFileSync(path.join(P.dir, "meta.json"), JSON.stringify({ id: slug, name: ep.topic }, null, 2) + "\n");

const base = fs.readFileSync(path.join(TEMPLATES, "scenes/_base.html"), "utf8");
const total = ep.scenes.reduce((n, s) => n + s.timing.duration, 0);

function fill(tpl, vars) {
  return tpl.replace(/\{\{(\w+)\}\}/g, (m, k) => (k in vars ? vars[k] : m));
}

let written = 0;
for (const [i, scene] of ep.scenes.entries()) {
  const frag = fs.readFileSync(path.join(TEMPLATES, `scenes/${scene.template}.html`), "utf8");
  const style = frag.match(/<style>([\s\S]*?)<\/style>/)?.[1] ?? "";
  const script = frag.match(/<script>([\s\S]*?)<\/script>/)?.[1] ?? "";
  const renderDuration = renderDurationOf(ep, i);
  const data = {
    id: scene.id,
    template: scene.template,
    onScreen: scene.onScreen,
    highlight: scene.onScreen.highlight ?? [],
    showCaptions: scene.onScreen.showCaptions ?? true,
    words: scene.timing.words,
    speechEnd: scene.timing.speechEnd,
    duration: scene.timing.duration,
    renderDuration,
    globalStart: scene.timing.start,
    total: round3(total),
  };
  const contentHash = crypto
    .createHash("sha1")
    .update(base + frag + JSON.stringify(data) + JSON.stringify(ep.theme))
    .digest("hex")
    .slice(0, 12);

  const out = path.join(P.scenes, `${scene.id}.html`);
  if (fs.existsSync(out) && !FORCE) {
    const head = fs.readFileSync(out, "utf8").match(/autoshorts:(generated|custom)[^>]*/)?.[0] ?? "";
    if (head.includes("autoshorts:custom")) {
      console.log(`= ${scene.id} custom 씬 — 건너뜀 (duration 확인: ${renderDuration}s)`);
      continue;
    }
    if (head.includes(`hash=${contentHash}`)) {
      console.log(`= ${scene.id} 변경 없음`);
      continue;
    }
  }
  // onScreen.bgImage → 정적 <img> (렌더 전에 로드되도록 HTML 에 직접 넣는다). 경로는 에피소드 폴더 기준 media/…
  const bgImage = scene.onScreen.bgImage;
  if (bgImage && !fs.existsSync(path.join(P.dir, bgImage))) throw new Error(`${scene.id} bgImage 없음: ${bgImage}`);
  const dim = scene.onScreen.bgDim ?? 0.6;
  const bgLayer = bgImage
    ? `<img class="bgimg" src="${bgImage}" alt="" />\n        <div class="bgshade" style="background: linear-gradient(180deg, rgba(0,0,0,${dim * 0.4}) 0%, rgba(0,0,0,${dim}) 45%, rgba(0,0,0,${Math.min(1, dim + 0.25)}) 100%)"></div>`
    : "";
  const html = fill(base, {
    bgLayer,
    ...ep.theme,
    id: scene.id,
    renderDuration,
    marker: `autoshorts:generated hash=${contentHash} template=${scene.template}`,
    sceneJson: JSON.stringify(data, null, 2).replace(/</g, "\\u003c"),
    templateStyle: style.trim(),
    templateScript: script.trim(),
  });
  fs.writeFileSync(out, html);
  written++;
  console.log(`▶ ${scene.id} (${scene.template}, ${renderDuration}s) 생성`);
}

// 미리보기용 전체 합본 (HyperFrames Studio 에서 음성과 함께 확인)
const index = `<!doctype html>
<html lang="ko" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="vendor/gsap.min.js"></script>
    <style>* { margin: 0; padding: 0; } html, body { width: 1080px; height: 1920px; overflow: hidden; background: ${ep.theme.bg}; }</style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="${round3(total)}" data-width="1080" data-height="1920">
${ep.scenes
  .map(
    (s) =>
      `      <div id="scene-${s.id}" class="clip" data-composition-id="${s.id}" data-composition-src="scenes/${s.id}.html" data-start="${s.timing.start}" data-duration="${s.timing.duration}" data-track-index="0"></div>`,
  )
  .join("\n")}
      <audio id="narration" src="audio/narration.mp3" data-start="0" data-duration="${round3(total)}" data-track-index="1"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {};
      window.__timelines["main"] = gsap.timeline({ paused: true });
    </script>
  </body>
</html>
`;
fs.writeFileSync(path.join(P.dir, "index.html"), index);
console.log(`✓ 씬 ${written}개 갱신 / 전체 ${ep.scenes.length}개, 총 ${round3(total)}s`);
