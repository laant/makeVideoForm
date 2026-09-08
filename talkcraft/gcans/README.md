# talkcraft/gcans — myNextSeason 프로덕션 연결

**상위주제·연출 규칙은 [`../../docs/PRODUCTION.md`](../../docs/PRODUCTION.md)를 따른다.** (⚠️ talkcraft는 비상업 라이선스 — 실험 전용)

- 아키텍처: talkcraft-demo 계승 (Rig 월드캔버스 + 카드 + Subtitles + timing.json 앵커)
- 건축쇼츠 전용 카드: `remotion/src/cards/dimension-counter.tsx`(계측선 코드 구현),
  `cross-section.tsx`(단면도 SVG 월드) — 계측선은 수치 발화 앵커에만 (마스터 문서 규칙)
- 렌더: `cd remotion && npx remotion render src/entry.ts GCans out/final.mp4`
