# dasongtax-news

다송세무회계 홈페이지(https://dasongtax.co.kr) "판례·세무 뉴스" 칸에 표시되는 데이터입니다.

- `news.json`: 매일 12시 예약 작업이 갱신합니다.
  - `cases`: 법원 판결·조세심판원 결정 (최대 4건, 원문 링크 필수)
  - `news`: 세무 뉴스 제목·언론사·링크 (최대 8건, 본문 미포함)

- `checkups-queue.json`: 평일 세법 리서치 작업이 쌓아 두는 "이런 분은 검토해 보세요" 공개용 요약 대기열(홈페이지에 표시 안 됨).
- `news.json`의 `checkups`: 매주 금요일 판례·뉴스 갱신 때 대기열을 옮겨 누적(최신순, 삭제하지 않음). 각 항목: id, date, tax, title, targets[], benefit, keywords[], basis.
- `checkups.js`: 홈페이지 표시용 위젯(면책 문구 포함). `<div id="dasong-checkups"></div>` + jsDelivr 스크립트.
