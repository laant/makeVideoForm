# 둥크(doongk) — ink-theater 엔진 연결

원화·규격: `mascot-template-round-crossbody.svg` · `CHARACTER-SPEC-round-crossbody.md`
엔진 플러그인: **`doongk.js`** (이 폴더) · 엔진 렌더 포즈 시트: `pose-sheet-doongk-engine.png`

## 쓰는 법 (HyperFrames 프로젝트)

1. `doongk.js` 를 프로젝트 폴더에 복사하고 `ink-theater.js` 다음에 불러온다.
   ```html
   <script src="ink-theater.js"></script>
   <script src="doongk.js"></script>
   ```
2. 기본 마스코트 대신 `InkTheater.doongk()` 를 쓴다. 사용법은 `mascot()` 와 같다.
   ```js
   var D = InkTheater.doongk({ x: 540, y: 1200, scale: 2.4 });  // (x,y) = 몸 중심, scale 2 = 원화 크기
   svg.appendChild(D.g);
   D.reachR([800, 1100]);           // 손끝 목표(화면 좌표) → 팔 2마디 IK, 몸 안으로 오면 자동으로 팔을 몸 앞에
   ```
3. 추가 기능
   | 함수 | 하는 일 |
   |---|---|
   | `D.legs([x,y],[x,y])` | 발끝 목표 → 다리 2마디 IK(무릎 바깥으로). 누르기·쪼그리기·앉기 |
   | `D.walk(phase)` | 정면 걷기 한 주기(0~1). 반환값 = 몸 상하 이동(화면 px) → `D.moveTo(x, y + 반환값)` |
   | `D.look(dx)` | 두 점눈을 함께 이동(−4~4) |
   | `D.mouth("smile" \| "o" \| "none")` | 작은 웃는 입 / 놀란 입 / 없음 |
   | `D.armFront("L"\|"R", true/false)` | 팔을 몸 앞/뒤로(자동 처리를 덮어쓸 때) |
   | `D.moveTo(x, y)` · `D.rest()` | 몸 이동 · 기본 자세로 |
   | `D.blink()` | 아무것도 안 함 — **점눈 유지 규칙** |

## 기본 마스코트에서 바꿔 끼울 때

- 둥크는 선이 가늘어(굵기 4 × scale/2) 같은 scale 이면 작아 보인다 → **1.3배** 권장.
- 발끝(바닥선)을 맞추려면 몸 중심을 `y + 70·s − 101·(1.3·s)` 로 둔다(s = 기존 마스코트 scale).
  ```js
  function mascot(x, y, s) { var z = s * 1.3; return InkTheater.doongk({ x: x, y: y + 70 * s - 101 * z, scale: z }); }
  ```
- 키가 커지므로(다리가 몸통만큼 김) 주변 글자·사물과 겹치는지 정지 화면으로 확인하고 위치를 옮긴다. 팔을 늘리지 말고 캐릭터 위치를 조정.

## 검수 상태 (2026-10-07)

- 연결용 8종: 엔진으로 렌더해 원화 포즈 시트와 대조 — `pose-sheet-doongk-engine.png`
- 실제 장면: 29번 Flow Music 전체를 둥크로 바꾼 비교판 — `experiments/projects/ink-flow-music-doongk/`, 결과 `output/29-google-flow-music-plugin/ink-doongk_final_send.mp4` · `character-compare-sheet.jpg`
- 디자인 기준 12포즈 중 앉기·쪼그리기·달리기·점프·춤은 프리셋 함수가 아직 없음 — `legs()`·`moveTo()`·`reach*()` 조합으로 장면에서 직접 잡는다(필요해지면 프리셋 추가).
- 이름·성격·사용 권리(상업 이용) 항목은 규격 문서에서 아직 '미정'.
