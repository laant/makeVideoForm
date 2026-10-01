# 네이버 클립 업로드 (Aside 브라우저)

채널: https://clip.naver.com/@some____uuuu · 관리: https://clipcreators.naver.com (Aside 브라우저에 네이버 로그인 상태 유지)
네이버 클립은 공개 업로드 API 가 없어 Claude 가 Aside 로 웹 폼을 채운다. **'등록' = 즉시 전체 공개** 이므로 사용자 업로드 요청이 있을 때만 누른다.

## 1. 준비
```bash
cd autoShorts && npm run clip -- <프로젝트> --module <모듈> [--title N] [--session <Aside pwd()>]
```
- 영상·커버(thumb1)를 Aside 세션 폴더 `upload/` 로 복사 — Aside 는 세션 폴더 밖 파일을 `setInputFiles` 할 수 없다.
- 세션 폴더는 REPL `pwd()` 값. 생략하면 `~/.aside/u/0/sessions` 의 최신 폴더.
- titles.txt ★ 제목으로 **300자 설명**(제목 · 요약 · 블로그 안내 · ※고지 첫 문장 · 해시태그 5개) → `output/<프로젝트>/naverclip-plan.json`

## 2. 폼 채우기 (clipcreators 대시보드 → 업로드 → 동영상 업로드)
| 항목 | 방법 |
|---|---|
| 파일 | `input[type=file]` 에 `upload/<프로젝트>.mp4` (인코딩은 백그라운드) |
| 설명 * | textbox "설명 *" 에 plan.description — 해시태그는 자동으로 태그 칩이 된다. **제목 칸은 없다** |
| 커버 * | `input[accept="image/jpeg,image/png"]` 에 `upload/<프로젝트>-thumb.jpg` → 첫 커버로 선택됨 |
| 카테고리 * | 1차·2차 버튼 (예: 뷰티›스킨케어, 경제, 테크, 여행 …) |
| AI 활용 | AI 음성·생성 이미지를 썼으면 켬 |
| 광고·협찬 | 쇼핑커넥트 태그를 달면 자동으로 켜짐 |
| 정보 태그 | 쇼핑커넥트: 최근 링크 발급 상품 목록에서 **1개**(카테고리당 1개, 최대 5개) · 장소: 여행·장소 영상 |
| 콘텐츠 링크 | 블로그: **내 블로그 글**만 선택 가능 (원문이 내 블로그면 연결) |
| 공개 | 기본 전체 공개 · 필요하면 '등록 예약' |

## 3. 등록 후
```bash
npm run clip -- <프로젝트> --module <모듈> --log [--url <클립 주소>]
```
`publish-log.json` 의 `naverclip` 에 기록(재등록 시 이전 기록은 `naverclipHistory`).

## 실측 메모 (2026-09-30, 16번 첫 업로드)
- 등록 직후 콘텐츠 목록에 '공개'로 뜨지만 프로필 페이지 노출은 처리 후.
- 등록하면 '해피빈 기부콩' 팝업 — 닫기.
- **목록에서 '선택'은 순서로 누르지 말 것** — 쇼핑커넥트 상품·내 블로그 글 목록은 최신순이라 새 글/새 링크가 생기면 순서가 바뀐다(17번 때 첫 번째 '선택'이 다른 글(써모스)을 연결). 항목 이름으로 찾아 그 옆 '선택'을 누르고, 선택 후 태그·링크 이름을 다시 확인한다.
