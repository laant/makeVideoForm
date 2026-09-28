// episode.json + templates/scenes → episodes/<slug>/scenes/sNN.html (+ 미리보기용 index.html)
//   npm run scenes -- <slug> [--force]
// 생성 파일 첫 주석이 "shopshorts:generated" 이면 데이터/템플릿 변경 시 자동 갱신.
// Claude/사람이 직접 연출을 고친 씬은 주석을 "shopshorts:custom" 으로 바꾸면 덮어쓰지 않는다. (--force 는 무시하고 덮어씀)
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { ROOT, TEMPLATES, episodePaths } from "./lib/paths.js";
import { loadEpisode, requireTiming, renderDurationOf, slugArg, hasFlag, disclosureBanner, missingDisclosure } from "./lib/episode.js";
import { round3 } from "./lib/proc.js";

const slug = slugArg();
const FORCE = hasFlag("force");
const ep = loadEpisode(slug);
requireTiming(ep);
const miss = missingDisclosure(ep);
if (miss.length) {
  console.error(`고지 누락 — 씬을 만들 수 없다:\n${miss.map((m) => `  - ${m}`).join("\n")}`);
  process.exit(1);
}
const BANNER = disclosureBanner(ep);
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

const esc = (t) => String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

// 1층: 상단 고정 헤더. title 이 비면 렌더하지 않는다(그때는 stage 가 원래 위치로 올라간다).
const H = ep.header ?? {};
const HAS_HEADER = Boolean(H.title);
const TOPBAR = HAS_HEADER
  ? `<div class="topbar">
          <div class="tb-row">
            ${H.kicker ? `<div class="tb-kicker">${esc(H.kicker)}</div>` : ""}
            ${H.badge ? `<div class="tb-badge">${esc(H.badge).replace(/\n/g, "&#10;")}</div>` : ""}
          </div>
          <div class="tb-title">${esc(H.title).replace(/\n/g, "&#10;")}</div>
          <div class="tb-underline"></div>
        </div>`
  : "";

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
    productId: scene.productId ?? null,
    banner: BANNER,
    header: HAS_HEADER ? H : null,
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
    const head = fs.readFileSync(out, "utf8").match(/shopshorts:(generated|custom)[^>]*/)?.[0] ?? "";
    if (head.includes("shopshorts:custom")) {
      console.log(`= ${scene.id} custom 씬 — 건너뜀 (duration 확인: ${renderDuration}s)`);
      continue;
    }
    if (head.includes(`hash=${contentHash}`)) {
      console.log(`= ${scene.id} 변경 없음`);
      continue;
    }
  }
  // 배경: onScreen.bgVideo(Higgsfield 클립) 우선, 없으면 bgImage. 경로는 에피소드 폴더 기준 media/…
  // HyperFrames 는 <video> 를 네이티브로 처리한다(data-media-start 로 시작 지점 지정, 오디오는 끈다).
  const bgVideo = scene.onScreen.bgVideo;
  const bgImage = scene.onScreen.bgImage;
  if (bgVideo && !fs.existsSync(path.join(P.dir, bgVideo))) throw new Error(`${scene.id} bgVideo 없음: ${bgVideo}\n  → npm run clips -- ${slug}`);
  if (bgImage && !fs.existsSync(path.join(P.dir, bgImage))) throw new Error(`${scene.id} bgImage 없음: ${bgImage}`);
  const dim = scene.onScreen.bgDim ?? 0.6;
  // 정지 이미지는 위를 밝게 남겨도 되지만, 상품 클립은 밝은 배경이 많아 더 고르게 눌러야 라벨이 읽힌다
  const top = bgVideo ? dim * 0.8 : dim * 0.4;
  const mid = bgVideo ? Math.min(1, dim + 0.08) : dim;
  const shade = `<div class="bgshade" style="background: linear-gradient(180deg, rgba(0,0,0,${top}) 0%, rgba(0,0,0,${mid}) 45%, rgba(0,0,0,${Math.min(1, dim + 0.25)}) 100%)"></div>`;
  let bgLayer = "";
  if (bgVideo) {
    // 클립이 씬보다 짧으면 마지막 프레임에서 멈춘다(HyperFrames 기본). 루프가 필요하면 clips.js 에서 길이를 맞춘다.
    const mediaStart = scene.onScreen.bgVideoStart ?? 0;
    // data-start/-duration 은 HyperFrames 가 재생을 소유하기 위해 필수(없으면 media_missing_data_start 로 lint 실패).
    // data-media-start 는 소스 클립에서 잘라 쓸 시작 지점.
    bgLayer = `<video id="${scene.id}-bgvid" class="bgvid" src="${bgVideo}" data-start="0" data-duration="${renderDuration}" data-media-start="${mediaStart}" data-volume="0" muted playsinline></video>\n        ${shade}`;
  } else if (bgImage) {
    bgLayer = `<img class="bgimg" src="${bgImage}" alt="" />\n        ${shade}`;
  }
  const html = fill(base, {
    bgLayer,
    banner: BANNER,
    topbar: TOPBAR,
    rootClass: HAS_HEADER ? "" : " no-header",
    ...ep.theme,
    id: scene.id,
    renderDuration,
    marker: `shopshorts:generated hash=${contentHash} template=${scene.template}`,
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
