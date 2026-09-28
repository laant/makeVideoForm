# talkcraft — 코드 모션그래픽 모듈 (동결)

**상위 문서: [`../docs/PRODUCTION.md`](../docs/PRODUCTION.md)**

> ## ⚠️ 동결 — 신규 제작은 autoShorts 를 쓴다 (2026-09-23)
>
> 라이선스가 **PolyForm Noncommercial 1.0.0** 이라 수익화 채널용 제작에 쓸 수 없다.
> 라이선스 고지 원문: *"Videos produced with this toolkit belong to their creators.
> This license governs the toolkit itself: noncommercial use is free; any commercial use
> of the toolkit requires prior authorization."*
> → **이미 만든 영상(01·03·04·05 등)의 소유권은 우리에게 있다.** 제약은 툴킷을 계속 쓰는 데 걸린다.
>
> **공통 모션 카드 4종은 autoShorts 로 이식 완료**(Apache-2.0 HyperFrames):
> `number-slab-pop` · `number-counter` · `alt-block-lines` · `strike-and-replace`
> → `autoShorts/templates/scenes/` · 사용법은 그 폴더의 `README.md`
>
> 이식 근거: `OpenMontage/.agents/skills/remotion-to-hyperframes` 의 `lint_source.py` 를
> 6개 프로젝트 전부에 돌려 **blocker 0** 확인(경고는 `useMemo` 2건·`staticFile()` 2건뿐).
> `useState`/`useEffect`/async `calculateMetadata`/서드파티 React UI 라이브러리 없음.
>
> **이식하지 않은 것**: 프로젝트 전용 월드 카드 7종
> (`cross-section` `dimension-counter` `paper-city` `taegukgi` `timeline-world` `money-world` `structure-world`).
> 특정 주제에서만 쓰여 재사용 가치가 낮다. 필요해지면 HyperFrames 네이티브로 새로 만든다
> — `taegukgi` 는 이미 autoShorts 의 `H.taegukgi()` 로 재현돼 04번에 쓰였다.
>
> 과거 프로젝트 재렌더가 필요하면 이 폴더는 그대로 남아 있다.

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
