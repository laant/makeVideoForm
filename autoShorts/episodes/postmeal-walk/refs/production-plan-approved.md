# 식후 걷기 — 제작 검토안

작성: 2026-10-01. 사용자 요청: 1번 식후 걷기, B안 연출, 전문 설명 1~2컷 추가.
상태: 대본·이미지 프롬프트 확인 대기. 업로드 미승인.
제안 제목: 몇 분 걸으면 혈당이 내려갈까?
제목 대안: 식후 10분 걷기, 혈당에 생기는 변화
사용자 제안 ‘몇 분이면 혈당 정상화’는 정상 수치 도달을 보장하는 뜻으로 읽혀 사용하지 않는다.
길이 목표: 45~55초, 실제 TTS 이후 확정. 인물 실사 3장 + 코드 기반 전문 설명 2컷.

## 컷별 대본과 연출

| 컷 | 나레이션 | 화면 |
|---|---|---|
| 1 | 식후에 걷는 십 분, 혈당 관리에 도움이 될 수 있습니다. | 식사를 마친 인물, ‘식후 10분’과 신발을 향하는 시선. 특정 시간 내 정상화 보장 없음. |
| 2 | 걷는 동안 근육이 혈액 속 포도당을 에너지로 쓰기 때문인데요. | 전문 컷 1. 혈관→포도당→수축하는 근육을 단순화한 모션 도식. ‘원리 설명용 도식’ 표기. |
| 3 | 제이형 당뇨병 성인 마흔한 명을 대상으로 한 연구에서는, | 전문 컷 2 시작. 41명 · 제2형 당뇨병 · 무작위 교차시험 표기. |
| 4 | 하루 삼십 분 걷기보다, 매 끼니 뒤 십 분씩 걸을 때 식후 혈당 상승의 누적 지표가 약 십이 퍼센트 낮았습니다. | 같은 연구 컷 연속. 30분/일 vs 10분×3회. 비교 지표 100 vs 88의 정규화 막대. ‘식후 3시간 증분곡선하면적(iAUC)’ 및 ‘2주씩 비교 · Reynolds et al., 2016’. 혈당 수치나 피크가 12% 감소한 것으로 표시하지 않음. |
| 5 | 하지만 십 분 만에 혈당이 정상화된다는 뜻은 아닙니다. | 산책 실사 + ‘효과는 사람마다 다릅니다’. 정상화 시간 카운트다운이나 가짜 CGM 그래프 없음. |
| 6 | 오늘은 식사 뒤, 편안한 속도로 짧게 걸어보세요. | 보폭·운동화 클로즈업에서 산책 전신으로 전환. |
| 7 | 인슐린이나 일부 당뇨약을 쓴다면, 저혈당 예방 방법을 의료진과 확인하세요. | 밝고 차분한 산책 마무리, 핵심 주의문을 읽기 쉽게. |
| 8 | 다음 식사 뒤에 떠올릴 수 있게, 저장해 두세요. | 식탁→운동화 연결 모티프, 저장 CTA. |

## 근거 검증

1. https://pubmed.ncbi.nlm.nih.gov/27747394/
   Reynolds et al., Diabetologia 2016; 41명 제2형 당뇨병 성인, 각 중재 2주. 30분/일 조언과 매 주요 식사 뒤 10분 걷기 조언 비교. 식후 3시간 혈당 iAUC 기하평균비 0.88(95% CI 0.78–0.99), 약 12% 감소. 혈당 농도 12% 감소 또는 정상화율이 아님. 일반 성인 모두에 동일 효과로 확대하지 않음.
2. https://diabetes.org/health-wellness/fitness/blood-glucose-and-exercise
   근수축 시 포도당 흡수·에너지 이용 및 인슐린 민감도 관련 설명. 약을 대신하거나 인슐린이 불필요해진다는 주장 금지.
3. https://www.niddk.nih.gov/health-information/diabetes/overview/healthy-living-with-diabetes
   인슐린·설포닐유레아 등 사용 시 운동 관련 저혈당 위험. 복용량을 임의 조절하라는 내용은 넣지 않음.
4. https://pubmed.ncbi.nlm.nih.gov/36715875/
   식후 운동의 급성 식후 혈당 반응에 대한 2023년 메타분석. 설명란 보조 출처.

## 생성 이미지 프롬프트 (확인용)

공통: 세로 실사 에디토리얼 사진, 자연광, 아이보리·올리브·살구, 실제 생활 같은 공간과 인물. 글자·숫자·브랜드·의료진 복장 없음. 인물 일관성은 첫 이미지 참조로 유지. 제목은 렌더러에서 오버레이. 전문 컷은 정확한 코드 도식으로 제작.

### 1. 식탁 — meal.png
Photorealistic editorial photograph for a vertical health short, portrait 9:16. An ordinary Korean woman in her early forties wearing a pale oatmeal cardigan over a cream T-shirt, at a modest contemporary Korean apartment dining table just after finishing a balanced everyday meal. She is calmly beginning to stand up from her chair, natural candid gesture. Simple bowls, a small amount of rice and vegetable side dishes, no exaggerated perfect diet styling. Warm afternoon window light, ivory and muted olive palette, premium magazine photography with realistic skin and hands. Place the woman primarily in the middle and lower portion, keep the upper third softly uncluttered for later typography. No text, no numbers, no labels, no logos, no medical props.

### 2. 산책 — walk.png
Use the first image only as a character and wardrobe reference. Photorealistic editorial portrait-format 9:16 photograph of the same Korean woman, same oatmeal cardigan and cream T-shirt, comfortable dark trousers and plain walking shoes, enjoying an easy unhurried walk on a quiet level neighborhood park path in early autumn. Full body visible, natural relaxed stride and arms, not running, no athletic performance pose. Dappled afternoon light, restrained olive foliage and warm ivory highlights, realistic anatomy, premium documentary lifestyle photography. Leave clean soft background in the upper third for later titles. No text, numbers, logos, medical devices or charts.

### 3. 첫걸음 — steps.png
Use the walking image as wardrobe and lighting reference. Photorealistic editorial detail photograph, portrait 9:16, of the same woman's comfortable plain walking shoes and lower trouser legs taking one relaxed step on a flat neighborhood path. A few early autumn leaves, warm side light, subtle natural motion in the trailing foot but crisp leading shoe, cinematic intimate framing, olive and warm neutral palette. Everyday approachable walking, not strenuous exercise. Space above the feet for later typography. No text, numbers, logos, medical symbols or visual claims of weight loss.

## 제작·납품

확인 후: 내장 imagegen 생성 → Gemini Aoede TTS → HTML/CSS/GSAP 직접 연출 → HyperFrames/FFmpeg → 최종 영상과 자막·숫자 싱크 검수.
자동 납품: 세로 MP4, 썸네일 2장, 카드뉴스, 제목·설명 15안, 출처·프롬프트·검수 기록.
신규 프로젝트 번호는 제작 시 output 목록을 다시 확인해서 배정. 기존 프로젝트·다른 작업 변경은 보존.

사용자 승인: “응 확정” — 2026-10-01. 대본·프롬프트 승인 완료.
