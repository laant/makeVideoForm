// 새 에피소드 폴더 + episode.json 뼈대 생성 → 입력 페이지 열기
//   npm run new -- <slug> ["주제"] [--no-intake] [--no-open]
import fs from "node:fs";
import path from "node:path";
import { ROOT, episodePaths } from "./lib/paths.js";
import { hasFlag, loadEpisode, slugArg } from "./lib/episode.js";
import { writeReferenceMd } from "./lib/brief.js";
import { run } from "./lib/proc.js";

const slug = slugArg();
if (!/^[a-z0-9-]+$/.test(slug)) throw new Error("slug 는 영문 소문자/숫자/하이픈만");
const topic = process.argv.slice(2).filter((a) => !a.startsWith("-"))[1] ?? "";
const P = episodePaths(slug);
if (fs.existsSync(P.json)) throw new Error(`이미 존재: ${P.json} → 입력 수정은 npm run intake -- ${slug}`);
fs.mkdirSync(P.refs, { recursive: true });
fs.mkdirSync(P.media, { recursive: true });
const ep = {
  slug,
  topic,
  audience: "",
  tone: "",
  cta: "",
  scenes: [
    { id: "s01", template: "title", narration: "훅 문장", onScreen: { title: "제목" }, sfx: [{ name: "whoosh", at: "start" }], transitionOut: "crossfade" },
    { id: "s02", template: "cta", narration: "CTA 문장", onScreen: { headline: "헤드라인", action: "팔로우" }, sfx: [], transitionOut: "cut" },
  ],
  caption: "",
  hashtags: [],
  upload: { title: "", instagram: true, youtube: true },
};
fs.writeFileSync(P.json, JSON.stringify(ep, null, 2) + "\n");
writeReferenceMd(loadEpisode(slug));
console.log(`✓ episodes/${slug}/ 생성`);

if (hasFlag("no-intake")) {
  console.log(`입력 페이지: npm run intake -- ${slug}`);
} else {
  await run(process.execPath, [path.join(ROOT, "scripts/intake.js"), slug, ...(hasFlag("no-open") ? ["--no-open"] : [])]);
}
