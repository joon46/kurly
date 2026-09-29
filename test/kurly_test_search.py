import re
from playwright.sync_api import sync_playwright, expect

BASE_URL = "https://www.kurly.com"

def run_search_tests():
    with sync_playwright() as p:
        # 1. 자동화 탐지 방지 브라우저 설정
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )
        
        context = browser.new_context(
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="ko-KR"
        )

        # navigator.webdriver 탐지 우회 스크립트 주입
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        page = context.new_page()

        print("==================================================")
        print("🚀 [컬리] 검색 기능(SH) 자동화 테스트 시작")
        print("==================================================")

        # --------------------------------------------------
        # 사전 조건: 메인 페이지 진입
        # --------------------------------------------------
        print("\n1. 메인 페이지 진입 중...")
        page.goto(BASE_URL)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        # 컬리 검색 입력창 및 검색 버튼 Selector 정의
        # ※ 실제 DOM 구조에 맞게 Selector 수정 필요
        search_input = page.locator("input[placeholder*='검색어']").first
        search_btn = page.locator("button#submit").first

        # --------------------------------------------------
        # [SH_01] 검색창 미입력 검색 시 예외 처리
        # --------------------------------------------------
        print("\n▶ [SH_01] 검색창 미입력 검색 예외 처리 테스트 시작")
        
        


        # 1. 검색창에 아무것도 입력하지 않고 검색 시도
        search_input.click()
        search_input.fill("")
        search_btn.click()
        page.wait_for_timeout(1000)

        # 2. 화면 내 안내 팝업 메시지 검증
        # '검색어를 입력해주세요' 문구를 가진 div 요소 찾기
        
        modal_notice = page.locator("div:has-text('검색어를 입력해주세요.')").first
        
        assert modal_notice.is_visible(), "SH_01 실패: '검색어를 입력해주세요.' div 팝업이 화면에 노출되지 않음"
        print(f"   🔎 div 팝업 텍스트 노출 확인: '{modal_notice.inner_text().strip()}'")

        print("   ✅ SH_01 성공: 미입력 검색 팝업 확인 완료!")

        # 3. div 내부의 '확인' 버튼 클릭하여 팝업 닫기
        confirm_button = page.locator("div:has-text('검색어를 입력해주세요.') button:has-text('확인'), div button:has-text('확인')").first
        assert confirm_button.is_visible(), "SH_01 실패: 팝업 내 '확인' 버튼을 찾을 수 없음"
        confirm_button.click()
        page.wait_for_timeout(500)

        # --------------------------------------------------
        # [SH_02] 검색어 입력 시 하단에 연관 검색어가 실시간 노출
        # --------------------------------------------------
        print("\n▶ [SH_02] 연관 검색어 실시간 노출 테스트 시작")
        
        # 1. 상단 검색창에 '라볶이' 입력
        search_input.click()
        search_input.fill("라볶이")
        page.wait_for_timeout(1000)  # 연관 검색어 API 응답 및 드롭다운 노출 대기

        # 2. 연관 검색어 레이어 및 '라볶이' 관련 추천 검색어 노출 검증
        related_keywords_container = page.locator(".related-keywords, .search-autocomplete, [role='listbox']").first
        related_item = page.locator("text='라볶이'").first

        assert related_keywords_container.is_visible() or related_item.is_visible(), \
            "SH_02 실패: 검색창 하단에 연관 검색어가 노출되지 않음"
        
        print("   ✅ SH_02 성공: '라볶이' 입력 시 연관 검색어 레이어 노출 확인")

        # --------------------------------------------------
        # [SH_03] 검색어 실행 시 해당 키워드에 대한 검색 결과 노출
        # --------------------------------------------------
        print("\n▶ [SH_03] 검색 실행 및 검색 결과 노출 테스트 시작")

        # 1. '라볶이' 검색 실행 (Enter 입력)
        search_input.press("Enter")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        # 2. 검색 결과 페이지 이동 및 키워드 검증
        current_url = page.url
        # URL에 '라볶이' 인코딩 문자열 또는 search/s_keyword 파라미터가 포함되어 있는지 검증
        assert "search" in current_url or "라볶이" in current_url, \
            f"SH_03 실패! 검색 결과 페이지로 이동하지 않음 (현재 URL: {current_url})"

        # 3. 검색 결과 페이지 내 타이틀 또는 검색결과 키워드 영역 검증
        search_result_header = page.locator("span:has-text('에 대한 검색결과'), .search-result-title").first
        assert search_result_header.is_visible(), \
            "SH_03 실패: '라볶이' 검색 결과 화면 및 관련 상품 목록이 노출되지 않음"

        print(f"   ✅ SH_03 성공: '라볶이' 검색 결과 페이지 정상 이동 확인 (URL: {current_url})")

        # --------------------------------------------------
        print("\n==================================================")
        print("🎉 모든 검색 기능 테스트 케이스 성공적으로 완료!")
        print("==================================================")

        context.close()
        browser.close()

if __name__ == "__main__":
    run_search_tests()