from playwright.sync_api import sync_playwright

def run_pdp_tests():
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

        # webdriver 탐지 우회 스크립트 주입
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        try:
            # 2. 컬리 상품 상세 페이지(PDP) 진입
            print("\n1. 컬리 상품 상세(PDP) 페이지 이동")
            # TODO: PLP 페이지 실행 (예시 : 수산/해산물).
            pdp_url = "https://www.kurly.com/categories/909" 
            page.goto(pdp_url)

            # 상품 중 하나의 PDP 페이지 진입
            page.locator("div.css-mfzoxt.css-1kkt86i.css-1r99qxv").first.click()

            
            # 네트워크 및 화면 로딩 완벽 대기
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(3000) # 화면이 완전히 그려질 때까지 3초 여유 대기

            print("   └ PDP 페이지 진입 완료:")

            # -------------------------------------------------------------
            # [PDP_01] 카테고리 랭킹 페이지 이동 테스트
            # -------------------------------------------------------------
            print("\n2. [PDP_01] '최대혜택가' 아코디언 클릭 -> 혜택 정보 펼침/접힘 동작 검증 테스트")
            
            # '최대혜택가' 아코디언 버튼 및 내부에 펼쳐지는 혜택 레이어 선택
            benefit_accordion_btn = page.locator("button.css-19k9b7o.ex5n6t25").first
            benefit_detail_content = page.locator("div.css-nngg1q.e1sf01br0").first

            # 1) 클릭하여 최대혜택가 상세 내역 펼치기
            benefit_accordion_btn.click(force=True)
            page.wait_for_timeout(1000) # 펼침 애니메이션 대기

            # 검증 1: 혜택 상세 정보 레이어가 화면에 노출되는지 확인
            assert benefit_detail_content.is_visible(), "PDP_01 실패! '최대혜택가' 버튼 클릭 후 상세 혜택 안내가 펼쳐지지 않았습니다."
            print("   └ 최대혜택가 상세 레이어 펼침 확인 완료")

            # 2) 다시 클릭하여 아코디언 접기
            benefit_accordion_btn.click(force=True)
            page.wait_for_timeout(1000)

            # 검증 2: 혜택 상세 정보 레이어가 다시 닫혀서 안 보이는지 확인
            assert not benefit_detail_content.is_visible(), "PDP_01 실패! '최대혜택가' 버튼 재클릭 후 상세 혜택 안내가 접히지 않았습니다."
            
            print("   ✅ PDP_01 성공: 최대혜택가 아코디언 토글(펼침/접힘) 동작 검증 완료!")


            # -------------------------------------------------------------
            # [PDP_02] 브랜드 페이지 이동 및 브랜드명 비교 테스트
            # -------------------------------------------------------------
            print("\n3. [PDP_02] 브랜드 클릭 -> 해당 브랜드 페이지 이동 및 브랜드명 검증 테스트")
            
            # div 안의 strong 태그에서 브랜드 이름 추출
            brand_element = page.locator("div.css-708at2 strong").first
            expected_brand_name = brand_element.inner_text().strip()
            assert expected_brand_name, "PDP_02 실패: PDP 페이지에서 브랜드 이름을 인식하지 못했습니다."
            print(f"   🔎 PDP strong 태그에서 인식한 브랜드 이름: '{expected_brand_name}'")

            # 브랜드 버튼 클릭
            brand_element.click(force=True)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(2000)

            # URL 검증
            current_url = page.url
            assert "brand" in current_url, f"PDP_02 실패! 브랜드 페이지 URL이 아닙니다. (현재 URL: {current_url})"

            # 브랜드 페이지 내 브랜드 이름 포함 여부 검증
            page_content = page.content()
            assert expected_brand_name in page_content, (
                f"PDP_02 실패! 브랜드 페이지에서 브랜드명('{expected_brand_name}')을 찾을 수 없습니다."
            )
            print(f"   ✅ PDP_02 성공: 브랜드 페이지 진입 및 브랜드명('{expected_brand_name}') 일치 확인 완료!")

            # 다음 케이스 수행을 위해 PDP로 복귀
            page.go_back()
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(2000)


            # -------------------------------------------------------------
            # [PDP_03] 후기 영역 스크롤 이동 테스트
            # -------------------------------------------------------------
            print("\n4. [PDP_03] '후기 00건' 버튼 클릭 -> 후기 영역 스크롤 이동 테스트")
            
            # '후기 00건' 버튼 클릭
            review_btn = page.locator("button:has-text('후기'), .css-1r968dw.e1we9rll1").first
            review_btn.click(force=True)
            page.wait_for_timeout(1500) # 스크롤 이동 대기

            # 후기 영역 요소 노출 검증
            review_section = page.locator("span:has-text('후기')").first
            assert review_section.is_visible(), "PDP_03 실패: 후기 영역이 화면에 노출되지 않음"
            
            # 스크롤 이동 위치(Scroll Y) 검증
            scroll_y = page.evaluate("window.scrollY")
            assert scroll_y > 0, f"PDP_03 실패: 스크롤이 하단으로 이동하지 않음 (현재 Scroll Y: {scroll_y})"
            print(f"   ✅ PDP_03 성공: 후기 영역으로 이동 확인 완료! (현재 Scroll Y: {scroll_y}px)")

            print("\n🎉 [PDP_01 ~ PDP_03] 모든 PDP 테스트케이스 정상 통과!")

        except Exception as e:
            print(f"\n❌ 테스트 중 에러 발생: {e}")

        finally:
            page.wait_for_timeout(2000)
            browser.close()
            print("🏁 브라우저 종료")

if __name__ == "__main__":
    run_pdp_tests()