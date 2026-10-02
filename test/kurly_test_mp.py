import re
from playwright.sync_api import sync_playwright, expect

BASE_URL = "https://www.kurly.com"

def run_main_page_tests():
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
        print("🚀 [컬리] 메인 페이지(MP_01 ~ MP_04) 자동화 테스트 시작")
        print("==================================================")

        # --------------------------------------------------
        # 사전 조건: 메인 페이지 진입
        # --------------------------------------------------
        print("\n1. 메인 페이지 진입 중...")
        page.goto(BASE_URL)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        # selector 정의
        popup_layer = page.locator("div[class*='popup'], div.lacms-popup-style-boundary").first
        popup_close_btn = page.locator("button:has-text('닫기'), button[class*='close']").first # 광고 닫기버튼
        
        # 배너 정지버튼, 배너 이전버튼, 
        banner_pause_btn = page.locator("button.css-htzo2l, button[aria-label*='pause'], .swiper-button-pause").first 
        banner_prev_btn = page.locator("button[direction='left'], .swiper-button-prev").first
        banner_pagination = page.locator("span.css-1icq3ng.css-okc7pe.css-35ezg3.css-16wi2x0, [class*='banner_page']").first
        
        # 마켓컬리, 뷰티컬리 이동버튼. 화면이 마켓컬리면 뷰티컬리 버튼의 class엔 active가 적혀있지 않음
        beauty_tab = page.locator("button.css-mxd3pm.e1fn5l9s1, button:has-text('뷰티컬리')").first
        beauty_active_tab = page.locator("button.active.css-mxd3pm.e1fn5l9s1, button:has-text('마켓컬리')").first

        # --------------------------------------------------
        # [MP_01] 광고 팝업 닫기 후 새로고침 시 광고 팝업 재노출 확인
        # --------------------------------------------------
        print("\n▶ [MP_01] 광고 팝업 닫기 및 새로고침 후 재노출 검증 시작")
        
        if popup_layer.is_visible():
            print("   1. 광고 팝업 닫기 클릭")
            popup_close_btn.click()
            page.wait_for_timeout(1000)
            assert not popup_layer.is_visible(), "MP_01 실패: 광고 팝업이 닫히지 않음"

        print("   2. 새로고침 수행 중...")
        page.reload()
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        assert popup_layer.is_visible(), "MP_01 실패: 새로고침 후 광고 팝업이 다시 노출되지 않음"
        print("   ✅ MP_01 성공: 새로고침 후 광고 팝업이 정상적으로 다시 노출됨")

        # MP_02 진행을 위해 팝업 닫기
        if popup_layer.is_visible():
            popup_close_btn.click()
            page.wait_for_timeout(500)

        # --------------------------------------------------
        # [MP_02] 롤링배너 일시정지 버튼 누르기 (배너가 멈추어야 함)
        # --------------------------------------------------
        print("\n▶ [MP_02] 롤링배너 일시정지 검증 시작")
        
        assert banner_pause_btn.is_visible(), "MP_02 실패: 롤링배너 일시정지 버튼을 찾을 수 없음"
        
        banner_pause_btn.click()
        


        # 2. 일시정지 버튼 클릭 전/후의 현재 페이지 번호 저장
        current_page_before = banner_pagination.inner_text().strip() if banner_pagination.is_visible() else ""
        print(f"   🔎 일시정지 클릭 시점 배너 번호/텍스트: '{current_page_before}'")

        # 3. 일반적인 롤링 주기(3~4초)보다 긴 시간 대기
        page.wait_for_timeout(4000)

        # 5. 4초 대기 후의 페이지 번호 추출
        current_page_after = banner_pagination.inner_text().strip() if banner_pagination.is_visible() else ""
        print(f"   🔎 4초 대기 후 배너 번호/텍스트: '{current_page_after}'")

        # 6. 두 번호가 동일한지 검증 (동일해야 배너가 멈춘 것)
        assert current_page_before == current_page_after, \
            f"MP_02 실패: 일시정지 버튼을 눌렀으나 배너가 자동으로 전환되었습니다. (전: {current_page_before} -> 후: {current_page_after})"

        print("   ✅ MP_02 성공: 4초 대기 후에도 페이지 번호가 동일하여 배너 정지 상태 정상 검증 완료!")

        # --------------------------------------------------
        # [MP_03] 롤링배너 번호가 1번일 때 이전 버튼 누르기 (맨 마지막 순번 배너 노출)
        # --------------------------------------------------
        print("\n▶ [MP_03] 롤링배너 무한 순환(Loop) 기능 검증 시작")

        # 1. 배너 번호가 1번이 될 때까지 이전/다음 클릭 또는 1번 도달 확인
        while banner_pagination.is_visible() and not banner_pagination.inner_text().strip().startswith("1"):
            banner_prev_btn.click()
        page.wait_for_timeout(500)

        # 2. 1번 상태에서 이전 버튼 클릭
        assert banner_prev_btn.is_visible(), "MP_03 실패: 배너 이전 버튼을 찾을 수 없음"
        banner_prev_btn.click()
        page.wait_for_timeout(1000)

        # 3. 맨 마지막 순번 배너 노출 검증 (예: "10" 또는 "10 / 10" 형태, 1이 아닌 번호로 전환)
        new_page_text = banner_pagination.inner_text().strip() if banner_pagination.is_visible() else ""
        assert new_page_text != "1" and new_page_text != "1 / 10", f"MP_03 실패: 이전 버튼 클릭 후 마지막 배너로 이동하지 않음 (현재: {new_page_text})"
        
        print(f"   ✅ MP_03 성공: 1번 배너에서 이전 버튼 클릭 시 마지막 배너 노출 확인 (변경 후: {new_page_text})")

        # --------------------------------------------------
        # [MP_04] '뷰티컬리' 버튼 클릭 (뷰티컬리 탭 활성화/보라색, 마켓컬리 탭 비활성화)
        # --------------------------------------------------
        print("\n▶ [MP_04] 상단 서비스 탭(뷰티컬리) 전환 및 UI 검증 시작")

        assert beauty_tab.is_visible(), "MP_04 실패: '뷰티컬리' 탭 버튼을 찾을 수 없음"
        
        # 1. 뷰티컬리 탭(버튼) 클릭
        beauty_tab.click()
        page.wait_for_timeout(3000)

        
        # 2. 클릭 후 뷰티컬리 버튼의 class 속성 가져오기
        beauty_class = beauty_tab.get_attribute("class") or ""
        print(f"   🔎 뷰티컬리 클릭 후 class 값: '{beauty_class}'")

        # 3. class 값에 'active'가 포함되어 있는지 확인
        assert "active" in beauty_class, f"MP_04 실패: '뷰티컬리' 버튼 class에 'active'가 포함되어 있지 않음 (현재 class: '{beauty_class}')"
        
        print("   ✅ MP_04 성공: '뷰티컬리' 버튼 class에 'active' 부여 정상 확인 완료!")

        context.close()
        browser.close()

if __name__ == "__main__":
    run_main_page_tests()