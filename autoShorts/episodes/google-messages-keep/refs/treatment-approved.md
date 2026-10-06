# Google 메시지 × Keep — 커플 장보기 쇼츠 제작안
작성일: 2026-10-05
상태: 대본·연출·이미지 프롬프트 확인 대기

## 콘셉트
블로그 첫 이미지의 커플을 같은 인물로 유지하는 약 40~45초 세로 일러스트 쇼츠. 노란 니트와 짙은 갈색 올림머리 여성, 남색 니트와 검은 웨이브 머리 남성의 장보기 상황을 통해 Google 메시지의 Keep 공유 메모 사용과 접근 권한을 설명한다. 직접 사용한 후기처럼 표현하지 않는다.

## 연결 모티프
노란 장보기 메모가 커플 사이에서 이어진다. 말풍선 → 공유 목록 → 공동작업자 카드로 변화한다.

## 팔레트·글꼴
원본의 크림 바탕·남색 글자·노란 강조색. 따뜻한 종이 질감과 부드러운 일러스트를 유지한다.
Pretendard 굵은 글꼴은 핵심 문구, 보통 굵기는 메뉴 경로와 출처. 하단 반복 자막 대신 화면 요약을 발화에 맞춘다.
실제 앱 UI를 모사하지 않고 설명용 카드임을 표시한다. AI 이미지 내 문자 없이 렌더러에서 정확한 한글을 추가한다.

## 대본·장면
|컷|나레이션|화면·연출|
|---|---|---|
|1|장보기 메시지, 이제 같은 목록에서 확인하세요.|원본 대표 이미지를 먼저 온전히 보여주고 같은 커플의 세로 구도로 전환. Google 메시지 × Keep, 같이 쓰는 장보기 메모.|
|2|구글 메시지 대화에서 추가, 킵 메모를 눌러 목록을 보내면 돼요.|여성이 휴대폰을 조작. 옆에 추가 → Keep 메모 → 보내기 설명 카드가 순서대로 등장. Android 기준 표시.|
|3|우유를 샀다면 직접 체크. 상대도 바뀐 목록을 볼 수 있어요.|마트의 남성이 우유를 담고 화면을 터치한 뒤 우유 항목 체크. 집에 있는 여성의 목록에도 체크가 반영되는 개념 연출. 자동 구매 추적처럼 보이지 않도록 조작 후 변화.|
|4|수정이 안 되면, 메모 주인에게 권한을 요청하세요.|여성이 상대에게 요청하고 남성이 확인. 수정 권한 확인 카드.|
|5|그런데 단체방을 나가도, 공유 메모는 계속 볼 수 있어요.|두 사람과 익명 모임 참가자 실루엣의 그룹 개념도. 실루엣은 방에서 빠지지만 메모 연결선은 남는다.|
|6|공유를 끝내려면 킵에서 공동작업자를 확인하고, 제외할 사람을 삭제한 뒤 저장하세요.|같은 커플이 메모의 공동작업자 카드를 확인. 선택한 사람의 접근 연결만 사라지고 메모는 유지된다.|
|7|내 대화창에 킵 메모가 있는지, 먼저 확인해 보세요.|커플이 장바구니를 정리하며 미소. 내 앱에서 메뉴 확인 문구와 블로그 안내로 마무리.|

## 컷별 이미지 생성 프롬프트
내장 image_gen 사용. 각 생성에 refs/couple-cover.webp를 캐릭터·스타일 참조로 제공한다. 원본을 처음 보여준 후 아래 파생 이미지로 연결한다.
공통 고정 조건:
Use the supplied illustration as the character identity and art-style reference. Preserve the exact same adult couple: woman with dark brown hair in a loose updo and a mustard-yellow knitted sweater, man with wavy black hair and a navy knitted sweater. Match their facial features, age, clothing, warm cream home atmosphere, soft painterly editorial illustration and subtle paper texture. Portrait 9:16 framing. Keep faces and essential actions in the central safe area with room for separately rendered captions. No text, letters, numbers, logos or real application UI. No additional identifiable people. Do not reproduce the original headline. Phones are generic with blank screens.

1. Couple together in the same warm kitchen, both holding their phones, a grocery tote on the counter, friendly engaged expressions. Medium two-shot, a clear central gap for a separately composited shared-list card.
2. Same woman in the kitchen using her ivory phone, friendly focused expression, medium three-quarter view. Clear negative space beside her for instruction cards.
3. Same man in a softly suggested grocery aisle holding a plain unbranded milk carton near a basket, actively tapping his black phone with his free hand. Natural plausible hands and phone grip, waist-up.
4. Same couple side by side at the kitchen counter checking their phones with thoughtful expressions, open central negative space for a permissions diagram.
5. Same couple smiling as they unpack groceries in the original warm kitchen. Ivory tote, milk carton and vegetables, waist-up composition, clean upper-middle room for closing text.
컷 3은 남성 이미지와 컷 2 여성 이미지를 분할해 수동 체크 동작과 동기화를 연출한다. 컷 4~6은 이미지 4를 사용하되 서로 다른 클로즈업·도식으로 변화시킨다.

## 팩트체크와 범위
- Google 공식 도움말 확인: 대화 → 추가 → Keep 메모 → 목록 작성 → 보내기.
- Android에서 미리보기는 수정 시 갱신. 수정 권한을 요청해야 할 수 있음.
- 그룹 채팅에서 나간 사용자도 메모 접근 가능.
- Keep → 작업 → 공동작업자 → 사용자 삭제 → 저장.
- 한국 모든 기기에 배포 완료라고 말하지 않음. iPhone에서 동일 작성 메뉴를 제공한다고 말하지 않음.
- 소유한 메모 자체를 삭제하면 모두에게 삭제되므로 영상에서는 사람의 접근 해제만 보여줌.
- 암호화 상세는 짧은 영상의 핵심에서 제외하고 설명에 원문 링크 제공.

출처:
https://pulluptech.blogspot.com/2026/10/google-messages-keep-notes.html
https://support.google.com/keep/answer/18080385?hl=ko
https://support.google.com/keep/answer/6101196?co=GENIE.Platform%3DAndroid&hl=ko

## 제작·납품
기존 B안 방식: 내장 이미지 생성 + 커스텀 HTML/CSS/GSAP + autoShorts Gemini Aoede 음성(gemini-3.1-flash-tts-preview, prompt 빈 문자열) + HyperFrames/FFmpeg.
1080×1920, 30fps. 발화 단어 기준 키워드 등장, 얼굴·텍스트 안전영역 검수, 음악 덕킹.
최종 영상·썸네일 2장·제목/설명·카드뉴스·프롬프트·출처·검수 기록. 업로드는 별도 요청 시에만.
