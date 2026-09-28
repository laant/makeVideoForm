// 인스타 카드뉴스: 씬 템플릿을 1080x1080 정지 이미지로 → cards/01.png …
//   npm run cards -- <slug> [--only s02]
// 영상과 같은 템플릿·테마·렌더러를 쓰되 자막·진행바를 빼고 모든 요소가 나온 최종 상태로 고정한다.
// 음성(timing)이 없어도 만들 수 있다. custom 씬도 템플릿 기준으로 만든다(커스텀 연출은 반영되지 않음).
import fs from "node:fs";
import path from "node:path";
import { ROOT, TEMPLATES, episodePaths } from "./lib/paths.js";
import { loadEpisode, slugArg } from "./lib/episode.js";
import { HF_BIN, run } from "./lib/proc.js";

const slug = slugArg();
const ep = loadEpisode(slug);
const P = episodePaths(slug);
const onlyIdx = process.argv.indexOf("--only");
const only = onlyIdx > 0 ? process.argv[onlyIdx + 1] : null;

const SIZE = 1080;
const src = path.join(P.cards, "src");
fs.mkdirSync(src, { recursive: true });
fs.mkdirSync(P.vendor, { recursive: true });
fs.copyFileSync(path.join(ROOT, "node_modules/gsap/dist/gsap.min.js"), path.join(P.vendor, "gsap.min.js"));

const CARD_STYLE = `
      .captions, .progress { display: none !important; }
      .stage { top: 90px; bottom: 150px; }
      .glow.a { top: -200px; } .glow.b { bottom: -200px; }
      /* 정지 화면에서는 비교의 '진 쪽'을 흐리게 두지 않는다 */
      .c-col.lose { opacity: 1 !important; }
      .c-col.lose .c-item { color: #d8d8e0 !important; }
      .c-col { transform: none !important; }
      .card-note {
        align-self: stretch; padding: 26px 32px; border-radius: 24px; border: 3px solid var(--accent);
        font-size: 42px; font-weight: 700; line-height: 1.35; white-space: pre-line;
      }
      .card-foot {
        position: absolute; left: 90px; right: 90px; bottom: 50px; display: flex; justify-content: space-between;
        align-items: flex-end; gap: 40px; font-family: var(--font); font-size: 28px; font-weight: 600; color: var(--muted);
      }
      .card-foot .page { flex: none; font-variant-numeric: tabular-nums; color: var(--fg); }`;

function replaceOnce(s, from, to) {
  if (!s.includes(from)) throw new Error(`_base.html 구조가 바뀌어 카드 변환 실패: ${from.slice(0, 40)}…`);
  return s.replace(from, to);
}

const esc = (t) => t.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" })[c]);

const base = fs.readFileSync(path.join(TEMPLATES, "scenes/_base.html"), "utf8");
const scenes = ep.scenes.filter((s) => s.onScreen.card !== false);

fs.rmSync(path.join(P.cards, ".frames"), { recursive: true, force: true });
for (const [i, scene] of scenes.entries()) {
  const n = String(i + 1).padStart(2, "0");
  if (only && scene.id !== only) continue;
  const frag = fs.readFileSync(path.join(TEMPLATES, `scenes/${scene.template}.html`), "utf8");
  const style = frag.match(/<style>([\s\S]*?)<\/style>/)?.[1] ?? "";
  const script = frag.match(/<script>([\s\S]*?)<\/script>/)?.[1] ?? "";
  const t = scene.timing;
  const data = {
    id: scene.id,
    template: scene.template,
    onScreen: scene.onScreen,
    highlight: [],
    showCaptions: false,
    words: t?.words ?? [],
    speechEnd: t?.speechEnd ?? 3,
    duration: t?.duration ?? 3,
    renderDuration: 1,
    globalStart: 0,
    total: 1,
  };

  let html = base
    .replaceAll("height: 1920px", `height: ${SIZE}px`)
    .replace('data-height="1920"', `data-height="${SIZE}"`)
    .replace("height=1920", `height=${SIZE}`);
  html = replaceOnce(html, "{{templateStyle}}", `{{templateStyle}}${CARD_STYLE}`);
  html = replaceOnce(
    html,
    '<div class="progress"></div>',
    `<div class="progress"></div>
        <div class="card-foot"><span>${esc(ep.cards.footer)}</span><span class="page">${i + 1} / ${scenes.length}</span></div>`,
  );
  html = replaceOnce(
    html,
    'window.__timelines["{{id}}"] = tl;\n      tl.seek(0);',
    `if (S.onScreen.cardNote) H.el("div", "card-note", S.onScreen.cardNote, stage);
      // 카드: 모든 요소가 나온 최종 상태로 고정하고, 렌더러에는 빈 타임라인을 넘긴다
      tl.progress(1);
      window.__timelines["{{id}}"] = gsap.timeline({ paused: true });`,
  );
  html = html.replace(/\{\{(\w+)\}\}/g, (m, k) => {
    const vars = {
      ...ep.theme,
      id: scene.id,
      renderDuration: 1,
      marker: `autoshorts:card template=${scene.template}`,
      sceneJson: JSON.stringify(data, null, 2).replace(/</g, "\\u003c"),
      templateStyle: style.trim(),
      templateScript: script.trim(),
      bgLayer: "", // 카드는 배경 그림 없이 (cards/src 경로에서 media/ 를 못 찾음)
    };
    return k in vars ? vars[k] : m;
  });
  const file = path.join(src, `${scene.id}.html`);
  fs.writeFileSync(file, html);

  console.log(`▶ ${n}.png ← ${scene.id} (${scene.template})`);
  const frames = path.join(P.cards, ".frames", scene.id);
  await run(
    HF_BIN,
    ["render", ".", "-c", path.relative(P.dir, file), "--format", "png-sequence", "-o", frames, "--fps", "1", "--quiet"],
    { cwd: P.dir, capture: true },
  );
  const png = fs.readdirSync(frames).filter((f) => f.endsWith(".png")).sort()[0];
  if (!png) throw new Error(`${scene.id} 카드 렌더 결과 없음`);
  // png-sequence 는 투명 배경(RGBA) → 테마 배경색 위에 합성
  await run("ffmpeg", [
    "-y", "-loglevel", "error",
    "-f", "lavfi", "-i", `color=c=${ep.theme.bg}:s=${SIZE}x${SIZE}`,
    "-i", path.join(frames, png),
    "-filter_complex", "[0][1]overlay=format=auto,format=rgb24", "-frames:v", "1",
    path.join(P.cards, `${n}.png`),
  ]);
}
fs.rmSync(path.join(P.cards, ".frames"), { recursive: true, force: true });

// 이전 실행에서 남은 번호(씬 수가 줄어든 경우) 정리
if (!only) {
  for (const f of fs.readdirSync(P.cards)) {
    const m = f.match(/^(\d{2})\.png$/);
    if (m && Number(m[1]) > scenes.length) fs.rmSync(path.join(P.cards, f));
  }
}
console.log(`✓ 카드 ${only ? 1 : scenes.length}장 → ${path.relative(process.cwd(), P.cards)}/`);
