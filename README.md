🛒 컬리(Kurly) 웹 E2E UI 자동화 테스트 포트폴리오
Playwright와 Python을 활용하여 컬리(Market Kurly) 웹사이트의 핵심 기능(로그인 예외 처리, PLP, 장바구니, 찜하기, 검색)을 자동화하고 검증하는 QA 프로젝트입니다.

🛠️ 기술 스택 및 환경 (Tech Stack)
Language: Python 3.x

Framework: Playwright (sync_api)

Browser Environment: Google Chrome (Headed Mode)

💡 주요 트러블슈팅 및 구현 기술 (Key Highlights)
1. 자동화 탐지 방지 (Bot Detection Bypass)
컬리 웹사이트의 봇 차단 방화벽 및 렌더링 제한을 우회하기 위해 Chrome 실행 옵션(--disable-blink-features=AutomationControlled)과 실제 사용자 User-Agent 스푸핑 설정을 적용하여 테스트 안정성을 확보

2. 동적 UI 및 예외 팝업 처리
React 기반 모달 팝업 탐색 시 난수형 CSS 클래스명 대신 ARIA 속성([role="dialog"]) 및 텍스트 조건(button:has-text("확인"))을 활용하여 구조 변화에 강한 Locator를 설계했습니다. 또한 팝업 노출 애니메이션 시간에 대응하기 위해 명시적 대기(wait_for(state="visible")) 및 강제 클릭(force=True) 옵션을 적용했습니다

🎯 주요 테스트 시나리오 (Test Scenarios)

1. 로그인 예외 처리 (kurly_test_login.py) <br>
웹사이트의 로그인 프로세스 및 예외 처리 팝업 동작을 검증합니다.
- [LOG_01] 미입력 상태 로그인 시도 예외 처리  아이디/비밀번호 미입력 후 로그인 클릭 시 예외 안내 팝업(role="dialog") 노출 및 텍스트 검증.
- [LOG_02] 잘못된 계정 정보 입력 예외 처리  존재하지 않는 계정 정보 입력 시 안내 팝업 노출 및 '확인' 버튼 동작 검증.
- [LOG_03] 비로그인 회원 전용 기능 접근 제어  비로그인 상태에서 상품 찜하기(하트) 클릭 시 로그인 유도 팝업 노출 검증.  

2. 상품 목록 페이지 (kurly_test_plp.py) <br>
웹사이트의 상품 리스트 영역에서 제공하는 정렬, 필터, 스크롤 편의기능이 요구사항에 맞춰 올바르게 동작하는지 검증합니다.

- [PLP_01] 정렬 옵션에서 '높은 가격순'을 선택할 때, 목록에 표시되는 상품들이 가격 오름차순/내림차순 기준에 맞춰 정상적으로 재정렬되는지 확인
- [PLP_02] 필터 적용: 'Kurly Only' 필터 선택 시 해당 조건 적용 여부 검증.
- [PLP_03] Top 버튼: 스크롤 이동 후 상단 이동 버튼 동작 검증.
- [PLP_04] 필터 초기화: 적용된 필터 조건 해제 기능 검증.
