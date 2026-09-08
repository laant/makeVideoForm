# myNextSeason 프로덕션 연결

이 저장소는 myNextSeason 쇼츠 프로젝트의 실행 모듈 중 하나다.
**상위주제·연출 프롬프트 템플릿·확인 게이트는 [`../docs/PRODUCTION.md`](../docs/PRODUCTION.md)를 따른다.**

- 진입 패턴: `projects/tokyo-gcans-archi/produce.py` (assets → props → render)
- 이미지 프롬프트는 마스터 문서의 건축쇼츠 템플릿(정지이미지 변형)을 적용:
  verbatim 블록 유지 · 계측선은 수치 컷만 · 숫자는 stat_card/kpi_grid 오버레이로
