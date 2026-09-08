# '건축 쇼츠' 프롬프트 템플릿 (2026-09-03 사용자 지정 · 이 구조·어휘·길이를 그대로 따를 것)

## 규칙 (항상 적용)

1. **템플릿 준수**: 아래 [프롬프트]와 똑같은 구조·어휘·길이로 작성하되, 내용만 해당 스크립트에 맞춘다.
2. **카메라**: 8초에 비트 2개까지. 사건(이벤트) 진행 중엔 **횡이동(lateral track)만**, 사건이 끝나면 **급속 푸시인 클로즈업** 후 홀드.
   - **멀티샷(2026-09-03 추가)**: 시작·끝(및 인접 무드컷)을 제외한 **설명 구간 컷은 8초 안 3샷 하드컷** 구성 — `CAMERA, SHOT ONE/TWO/THREE` + `HARD CUT.` 표기. 각 샷 안에서는 여전히 횡이동만, 마지막 샷이 푸시인 클로즈업 마무리. RED 계측선은 전 샷에 동일하게 지속(`persisting identically across every hard cut`).
3. **빨강**: 오직 계측선(치수선)으로만 사용. 매 컷 보조선(extension line)의 **고정/이동 여부를 명시**. 빨간 소품이 나오는 컷엔 계측선 금지(프레임 내 유일한 빨강 원칙).
   - **(2026-09-03 추가) 계측선은 대본에 명확한 수치가 있는 컷에만** 넣는다. 나레이션에 구체적 숫자(길이·깊이·개수·금액·연도 등)가 없는 컷은 RED 블록 자체를 생략 — 계측선이 잴 대상이 있어야 의미가 있음.
4. **납품 형식**: 한국어 설명 + 영문 코드블록 + 설정 표 + 글자수. 충돌(스타일·카메라 규칙·생성 난이도)은 미리 점검해 위험도와 함께 보고.

## 고정 verbatim 블록 (전 컷 토씨 불변)

- 오프닝: `A 8-second vertical 9:16 shot, semi-stylized 3D architectural visualization render sitting halfway between clean low-poly and photoreal.`
- STYLE: `STYLE: simplified readable geometry with real modeled detail, smooth shading with no visible polygon edges, matte materials with brushed steel, no mirror gloss, soft studio daylight with mild ambient occlusion, no sun disc.`
- COLOR 프레임: `COLOR IS RICH AND CLEAN: <소재 어휘 2~3개>, fully saturated, no gray wash and no desaturated grading.` (소재 어휘는 장면 그룹 내 verbatim)
- RED 꼬리: `They are the only saturated red in the frame and carry no numbers and no text.`
- 금지: `No text, no letters, no numbers, no labels, no logos, no watermark, no lens flare, no film grain, no vignette, no close-up faces.`
- 사운드 리드: `No background music. Only realistic location sound: <장면별 사운드>.`

## [프롬프트] 원문 (레퍼런스: 밀레니엄 브리지 비교 컷)

```
A 8-second vertical 9:16 shot, semi-stylized 3D architectural visualization render sitting halfway between clean low-poly and photoreal. SUBJECT: two bridge models standing side by side as technical models on a flat neutral pale gray studio ground with soft contact shadows, seen from a low three-quarter angle. The left one is the London Millennium Bridge, its suspension cables running almost flat and straight with only the shallowest sag between its Y-shaped piers. The right one is a conventional suspension bridge of the same length with deep swooping cables sagging far below tall towers. Everything else about them is identical, same white deck, same handrails, modeled anchor plates and turnbuckles at every cable end, clean empty studio space around them. STYLE: simplified readable geometry with real modeled detail, smooth shading with no visible polygon edges, matte materials with brushed steel, no mirror gloss, soft studio daylight with mild ambient occlusion, no sun disc. COLOR IS RICH AND CLEAN: bright white painted steel, pale neutral gray ground, fully saturated, no gray wash and no desaturated grading. CAMERA, BEAT ONE, the first two seconds: the camera tracks fast sideways from left to right past both models at a constant height. CAMERA, BEAT TWO, from two seconds to the end: the camera rushes in fast to a tight close-up on the almost flat cable of the left model, arriving by four seconds and holding locked off on it for the final second. RED: two pure red technical dimension annotations measure how far each cable sags below its anchor line, drafting style, on each model a thin horizontal extension line at the anchor height and another at the cable's lowest point with a vertical dimension line between them and a small sharp arrowhead at each end, glowing, the left one extremely short and the right one very tall, both holding their length for the whole shot. They are the only saturated red in the frame and carry no numbers and no text. No text, no letters, no numbers, no labels, no logos, no watermark, no lens flare, no film grain, no vignette, no close-up faces. No background music. Only realistic location sound: a thin metallic shimmer from the taut cables, quiet studio air, a fast air rush on the push-in.
```
