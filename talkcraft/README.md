# talkcraft — 코드 모션그래픽 모듈

**상위 문서: [`../docs/PRODUCTION.md`](../docs/PRODUCTION.md)** (⚠️ PolyForm Noncommercial — 실험 전용)

```
talkcraft/
├── video-talkcraft/   # 엔진·스킬 원본 (업스트림)
├── demo/              # 1호 숨은 보험금 (원조 데모 — node_modules 원본 보유)
├── gcans/             # 3호 도쿄 G-Cans (dimension-counter·cross-section 카드)
├── guri/              # 4호 구리 태극기 (taegukgi·paper-city 카드)
└── family/            # 5호 연안이씨 가족 (timeline-world 카드, 가로 16:9)
```

- 새 프로젝트: 기존 프로젝트 remotion/을 rsync(-a --exclude node_modules --exclude out)로 복제 후
  `ln -s ../../demo/remotion/node_modules remotion/node_modules`
- 렌더: `cd <프로젝트>/remotion && npx remotion render src/entry.ts <CompId> out/final.mp4`
- 오디오·타이밍: OpenMontage 프로젝트의 Aoede mp3를 concat → public/full.mp3 + src/timing.json (글자 비례 보간)
