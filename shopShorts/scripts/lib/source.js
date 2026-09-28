// source.json — 상품 원천 데이터. Claude 가 Aside 브라우저 자동화로 수집해 기록한다(CLAUDE.md 참조).
// 대본(episode.json)은 이 파일에서만 사실을 가져온다. 여기에 없는 수치는 영상에 쓰지 않는다.
import fs from "node:fs";
import { z } from "zod";
import { episodePaths } from "./paths.js";

export const SHOP_TYPES = ["a", "b", "c"];
export const TYPE_LABEL = {
  a: "제휴 리뷰형 (상품 URL + 리워드 링크 → 정보 정리)",
  b: "정보형 큐레이션 (주제 → 검색 → N선)",
  c: "단일 상품 홍보 (상품 URL + 리워드 링크)",
};

// 상품 이미지: Higgsfield 는 공개 URL 만 받으므로 원본 URL 을 반드시 보존한다.
const ProductImage = z.object({
  url: z.string().url(), // 상품 페이지의 공개 이미지 URL — i2v 입력으로 그대로 사용
  role: z.enum(["hero", "detail", "scale", "usage", "package"]).default("detail"),
  note: z.string().default(""),
});

export const Product = z.object({
  id: z.string().regex(/^p\d{2}$/, "상품 id 는 p01, p02 … 형식"),
  name: z.string().min(1),
  brand: z.string().default(""),
  url: z.string().url(), // 원본 상품 페이지 (출처)
  rewardUrl: z.string().default(""), // 사용자가 주는 리워드/제휴 링크
  price: z.object({
    current: z.number().nullable().default(null),
    original: z.number().nullable().default(null),
    currency: z.string().default("KRW"),
    note: z.string().default(""), // "쿠폰 적용가" 등
  }).prefault({}),
  rating: z.object({
    score: z.number().nullable().default(null),
    count: z.number().nullable().default(null),
  }).prefault({}),
  // 화면에 띄울 스펙. label/value 그대로 오버레이에 렌더된다
  specs: z.array(z.object({ label: z.string(), value: z.string() })).default([]),
  pros: z.array(z.string()).default([]),
  cons: z.array(z.string()).default([]),
  // 구매자 리뷰에서 반복되는 말 (요약이지 인용이 아님 — 원문 그대로 쓰지 않는다)
  reviewThemes: z.array(z.string()).default([]),
  images: z.array(ProductImage).default([]),
});

export const SourceSchema = z.object({
  slug: z.string().regex(/^[a-z0-9-]+$/),
  type: z.enum(SHOP_TYPES),
  topic: z.string().default(""), // b 타입: 큐레이션 주제
  products: z.array(Product).min(1),
  // 수집 시점 — 가격·스펙은 시간이 지나면 틀려지므로 고지에 그대로 쓴다
  collectedAt: z.string().min(1),
  collectedVia: z.string().default("aside"),
  notes: z.string().default(""),
});

export function loadSource(slug) {
  const p = episodePaths(slug);
  if (!fs.existsSync(p.source)) throw new Error(`source.json 없음: ${p.source}\n  → 먼저 상품 페이지를 수집할 것 (CLAUDE.md 참조)`);
  const parsed = SourceSchema.safeParse(JSON.parse(fs.readFileSync(p.source, "utf8")));
  if (!parsed.success) {
    throw new Error(`source.json 스키마 오류:\n${parsed.error.issues.map((i) => `  - ${i.path.join(".")}: ${i.message}`).join("\n")}`);
  }
  const ids = parsed.data.products.map((x) => x.id);
  if (new Set(ids).size !== ids.length) throw new Error("상품 id 중복");
  return parsed.data;
}

export function saveSource(src) {
  fs.writeFileSync(episodePaths(src.slug).source, JSON.stringify(src, null, 2) + "\n");
}

/**
 * 에피소드 전체에서 i2v 에 쓸 이미지 목록 (productId + 이미지).
 * key 는 media/<key>.mp4 파일명이 되므로 역할별로 번호를 매긴다 (hero, detail, detail2 …).
 */
export function clipCandidates(src) {
  return src.products.flatMap((p) => {
    const seen = {};
    return p.images.map((img) => {
      seen[img.role] = (seen[img.role] ?? 0) + 1;
      const n = seen[img.role];
      return { key: `${p.id}-${img.role}${n > 1 ? n : ""}`, productId: p.id, productName: p.name, ...img };
    });
  });
}
