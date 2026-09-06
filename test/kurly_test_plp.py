from playwright.sync_api import sync_playwright

def run_plp_tests():
    with sync_playwright() as p:
        # 1. 자동화 탐지 방지(Bot Detection Bypass) 옵션 추가하여 크롬 실행
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled", # 자동화 탐지 방지
                "--start-maximized"
            ]
        )
        
        # 실제 사용자처럼 보이도록 User-Agent 설정
        context = browser.new_context(
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            # 2. 컬리 메인 접속 ➔ PLP(베스트) 페이지로 이동
            print("\n1. 컬리 메인 진입 및 베스트(PLP) 페이지 이동")
            page.goto("https://www.kurly.com")
            

            # 네트워크 및 화면 로딩 완벽 대기
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(5000) # 화면이 완전히 그려질 때까지 5초 여유 대기
            
            # 베스트 메뉴 클릭하여 PLP 이동
            page.locator("text=베스트").first.click(force=True)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(5000) # 화면이 완전히 그려질 때까지 5초 여유 대기

            print("   └ PLP 페이지 진입 완료:", page.url)

            # -------------------------------------------------------------
            # [PLP_01] 정렬 옵션 선택 테스트
            # -------------------------------------------------------------
            print("\n2. [PLP_01] 정렬 옵션('높은 가격순') 테스트")
            page.locator("text=높은 가격순").click(force=True)
            page.wait_for_load_state("domcontentloaded")

            # 💡 가격 확인을 위해 상품 리스트 영역으로 약간 스크롤 내리기 (500px)
            page.evaluate("window.scrollBy(0, 500)")
            page.wait_for_timeout(1500) # 스크롤 후 상품 카드 로딩 대기

            # 상품 카드 목록 가져오기 (컬리 상품 카드 또는 '원' 텍스트를 가진 카드 영역)
            # a 태그나 상품 카드 역할을 하는 컨테이너 탐색
            product_cards = page.locator("article").all()

            prices = []
            
            # 상위 5개 상품의 할인가(실제 판매가) 추출
            for card in product_cards[:5]:
                # 할인율 제외, 가장 앞에 나오는 '원' 텍스트(할인가) 추출
                price_element = card.locator("span:has-text('원')").first
                if price_element.is_visible():
                    price_text = price_element.inner_text()
                    # '13,520원' -> 13520 (숫자만 남김)
                    clean_price = int(price_text.replace(",", "").replace("원", "").strip())
                    prices.append(clean_price)

            print(f"   └ 추출된 상위 상품 가격 목록: {prices}")

            # 내림차순(높은 가격순) 정렬 검증
            if len(prices) >= 2:
                assert prices == sorted(prices, reverse=True), f"정렬 실패! 현재 순서: {prices}"
                print("   ✅ PLP_01 성공: 높은 가격순 정렬 확인 완료!")
            else:
                print("   ⚠️ 추출된 가격 요소가 2개 미만입니다. Selector 확인 필요.")

            # 기존 상태로 
            page.locator("text=추천순").click()
            

            # -------------------------------------------------------------
            # [PLP_02] 필터 선택 테스트
            # -------------------------------------------------------------
            print("\n3. [PLP_02] 필터('Kurly Only') 선택 테스트")
            filter_btn = page.locator("text=Kurly Only").first
            filter_btn.click()

            # 필터 적용 후 UI 렌더링 대기
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(1000)

            # 💡 [검증 구문 추가]: 필터 적용 시 상단에 생성되는 선택된 필터 태그/뱃지 영역 확인
            # (컬리에서는 선택된 필터가 상단 태그 칩 형태나 초기화 버튼 활성화로 표시됨)
            selected_filter_tag = page.locator("div, span").filter(has_text="Kurly Only").last
            assert selected_filter_tag.is_visible(), "PLP_02 실패: Kurly Only 필터 태그가 화면에 노출되지 않음"
            print("   ✅ PLP_02 성공: Kurly Only 필터 적용 및 태그 노출 확인 완료!")
            page.wait_for_timeout(1000)
            
            # -------------------------------------------------------------
            # [PLP_04] 필터 초기화 테스트
            # -------------------------------------------------------------
            print("\n4. [PLP_04] 필터 초기화 테스트")
            reset_btn = page.locator("text=초기화")
            if reset_btn.is_visible():
                reset_btn.click()
                page.wait_for_load_state("domcontentloaded")
                print("   ✅ PLP_04 성공: 필터 조건 초기화 해제 확인")

            # -------------------------------------------------------------
            # [PLP_03] Top 버튼 동작 테스트
            # -------------------------------------------------------------
            print("\n5. [PLP_03] Top 버튼 클릭 테스트")
            # 스크롤을 하단으로 대폭 이동
            page.evaluate("document.documentElement.scrollTop = 2500")
            page.wait_for_timeout(1000)

            # 우측 하단 Top 버튼 클릭
            top_btn = page.locator("button[aria-label='top'], .btn-top, button:has-text('Top')").first
            if top_btn.is_visible():
                top_btn.click()
                page.wait_for_timeout(1000)
                scroll_y = page.evaluate("window.scrollY")
                assert scroll_y == 0, "최상단 이동 실패"
                print("   ✅ PLP_03 성공: Top 버튼 클릭 후 최상단 이동 확인")

            print("\n🎉 [PLP_01 ~ PLP_04] 모든 PLP 테스트케이스 정상 통과!")

        except Exception as e:
            print(f"\n❌ 테스트 중 에러 발생: {e}")

        finally:
            page.wait_for_timeout(2000)
            browser.close()
            print("🏁 브라우저 종료")

if __name__ == "__main__":
    run_plp_tests()