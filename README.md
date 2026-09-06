🛒 컬리(Kurly) 웹 E2E UI 자동화 테스트 포트폴리오
Playwright와 Python을 활용하여 컬리(Market Kurly) 웹사이트의 핵심 기능(로그인 예외 처리, PLP, 장바구니, 찜하기, 검색)을 자동화하고 검증하는 QA 프로젝트입니다.

🛠️ 기술 스택 및 환경 (Tech Stack)
Language: Python 3.x

Framework: Playwright (sync_api)

Browser Environment: Google Chrome (Headed Mode)

🎯 주요 테스트 시나리오 (Test Scenarios)

1. 로그인 예외 처리 (kurly_test_login.py) <br>
웹사이트의 로그인 프로세스 및 예외 처리 팝업 동작을 검증합니다.
- [LOG_01] 미입력 상태 로그인 시도 예외 처리  아이디/비밀번호 미입력 후 로그인 클릭 시 예외 안내 팝업(role="dialog") 노출 및 텍스트 검증.
- [LOG_02] 잘못된 계정 정보 입력 예외 처리  존재하지 않는 계정 정보 입력 시 안내 팝업 노출 및 '확인' 버튼 동작 검증.
- [LOG_03] 비로그인 회원 전용 기능 접근 제어  비로그인 상태에서 상품 찜하기(하트) 클릭 시 로그인 유도 팝업 노출 검증.  

2. 상품 목록 페이지 (kurly_test_plp.py) <br>
웹사이트의 상품 리스트 영역에서 제공하는 정렬, 필터, 스크롤 편의기능이 요구사항에 맞춰 올바르게 동작하는지 검증합니다.

- [PLP_01] 정렬 옵션에서 '높은 가격순'을 선택할 때, 목록에 표시되는 상품들이 가격 오름차순/내림차순 기준에 맞춰 정상적으로 재정렬되는지 확인
