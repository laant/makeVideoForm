// 새 쇼핑 쇼츠 에피소드 생성 — episode.json 뼈대 + source.json(상품 원천) 자리
//   npm run new -- <slug> <a|b|c> ["주제 또는 상품명"]
//
// a: 제휴 리뷰형 (상품 URL + 리워드 링크 → 정보 정리)
// b: 정보형 큐레이션 (주제 → 검색 → N선)
// c: 단일 상품 홍보 (상품 URL + 리워드 링크)
import fs from "node:fs";
import { episodePaths } from "./lib/paths.js";
import { slugArg } from "./lib/episode.js";
import { SHOP_TYPES, TYPE_LABEL } from "./lib/source.js";

const args = process.argv.slice(2).filter((a) => !a.startsWith("-"));
const slug = slugArg();
if (!/^[a-z0-9-]+$/.test(slug)) throw new Error("slug 는 영문 소문자/숫자/하이픈만");
const type = args[1];
if (!SHOP_TYPES.includes(type)) {
  console.error(`타입을 지정할 것: ${SHOP_TYPES.map((t) => `\n  ${t} — ${TYPE_LABEL[t]}`).join("")}\n\n  npm run new -- ${slug} a "상품명"`);
  process.exit(1);
}
const topic = args[2] ?? "";
const today = new Date().toISOString().slice(0, 10);

const P = episodePaths(slug);
if (fs.existsSync(P.json)) throw new Error(`이미 존재: ${P.json}`);
fs.mkdirSync(P.media, { recursive: true });
fs.mkdirSync(P.refs, { recursive: true });

// source.json — Claude 가 Aside 로 상품 페이지를 수집해 채운다 (CLAUDE.md 참조)
const source = {
  slug,
  type,
  topic,
  products: [
    {
      id: "p01",
      name: "",
      brand: "",
      url: "",
      rewardUrl: "",
      price: { current: null, original: null, currency: "KRW", note: "" },
      rating: { score: null, count: null },
      specs: [],
      pros: [],
      cons: [],
      reviewThemes: [],
      images: [],
    },
  ],
  collectedAt: "",
  collectedVia: "aside",
  notes: "",
};
fs.writeFileSync(P.source, JSON.stringify(source, null, 2) + "\n");

const ep = {
  slug,
  topic,
  shopType: type,
  audience: "",
  tone: "",
  cta: "",
  disclosure: {
    affiliate: type === "b" ? "" : "제휴 링크가 포함되어 있으며 구매 시 수수료를 받습니다",
    aiGenerated: "제품 영상은 AI로 생성되었습니다",
    source: `가격·스펙은 ${today} 기준`,
    banner: "",
  },
  links: [],
  scenes: [
    { id: "s01", template: "hook", narration: "훅 문장", onScreen: { title: "제목" }, sfx: [{ name: "whoosh", at: "start" }], transitionOut: "crossfade" },
    { id: "s02", template: "cta-link", narration: "CTA 문장", onScreen: { headline: "헤드라인", action: "설명란 링크 확인" }, sfx: [], transitionOut: "cut" },
  ],
  caption: "",
  hashtags: [],
  upload: { title: "", instagram: true, youtube: true },
};
fs.writeFileSync(P.json, JSON.stringify(ep, null, 2) + "\n");

console.log(`✓ episodes/${slug}/ 생성 — 타입 ${type} (${TYPE_LABEL[type]})`);
console.log(`
다음 순서:
  1. 상품 수집 → source.json 채우기 (Claude 가 Aside 로 수행, CLAUDE.md 참조)
  2. npm run clips -- ${slug} --dry     # 클립 후보 확인 (호출 없음)
  3. npm run clips -- ${slug}           # Higgsfield 생성 (유료)
  4. 대본 작성 → episode.json scenes (사용자 확인 게이트)
  5. npm run make -- ${slug}            # tts → scenes → render → assemble → verify`);
