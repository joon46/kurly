import re
from playwright.sync_api import sync_playwright

def run_cart_tests():
    with sync_playwright() as p:
        
        print("🔗 현재 로그인되어 켜져있는 크롬(127.0.0.1:9222)에 연결 중...")
        
        # IPv4 명시적 주소로 연결
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        
        # 현재 열려있는 탭 중에서 컬리 탭 찾기
        context = browser.contexts[0]
        page = None
        
        for p_item in context.pages:
            if "kurly.com" in p_item.url:
                page = p_item
                break
                
        if not page:
            page = context.pages[0]
            page.goto("https://www.kurly.com/cart")

        print(f"📌 현재 제어할 페이지: {page.url}")

        try:
            # =============================================================
            # [CART_01] 상품 상세에서 장바구니 담기
            # =============================================================
            print("\n1. [CART_01] 상품 상세 페이지 진입 및 장바구니 담기 테스트")
            
            # 테스트할 상품 상세 페이지로 직접 이동 (특정 카테고리 상품 중 1개 선택 또는 direct URL)
            #page.goto("https://www.kurly.com/categories/910")
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(1000)


            # 맨 처음으로 나오는 상품의 [담기] 버튼 클릭
            cart_btn = page.locator('button.css-nxe71v.css-w3rxu3').first
            cart_btn.wait_for(state="visible", timeout=5000)
            cart_btn.click(force=True)
            page.wait_for_timeout(1000)

            # 이후 장바구니 담기 버튼
            cart2_btn = page.locator('button:has-text("장바구니")').first
            cart2_btn.wait_for(state="visible", timeout=5000)
            cart2_btn.click(force=True)
            page.wait_for_timeout(1000)

            # 담기 성공 안내 토스트/팝업 또는 우측 상단 장바구니 배지 수량 변경 검증
            toast_msg = page.locator('div:has-text("장바구니에 상품을 담았습니다"), [role="dialog"]').first
            toast_msg.wait_for(state="visible", timeout=5000)
            
            assert toast_msg.is_visible(), "CART_01 실패: 장바구니 담기 안내 메시지 미노출"
            print("   ✅ CART_01 성공: 상품 상세에서 장바구니 담기 성공 메시지 확인 완료!")

            # =============================================================
            # [CART_02] 장바구니 수량 변경 및 금액 즉시 반영
            # =============================================================
            print("\n2. [CART_02] 장바구니 페이지 이동 및 수량 변경 테스트")
            
            # 상단 장바구니 아이콘 클릭하여 이동
            page.locator('button.css-1b4kx1j').first.click(force=True)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(1500)

            # 1. 수량이 표시된 p 태그 타겟팅 (div와 p 사이에 공백 필수!)
            count_elem = page.locator('div.kpds_j1jks20 p').first

            # 2. 버튼 클릭 전 초기 수량 읽기
            initial_count = int(re.sub(r'[^0-9]', '', count_elem.inner_text()))
            print(f"   - 초기 장바구니 수량: {initial_count}개")

            # 초기 단가/결제 금액 텍스트 추출
            #total_price_elem = page.locator('css-zorl92.ebe7z6d0').last # 결제예정금액
            #initial_price_text = total_price_elem.inner_text() # 수량 변경 전 금액
            #initial_price = int(re.sub(r'[^0-9]', '', initial_price_text))

            # -------------------------------------------------------------
            # 3. 수량 증가(+) 테스트
            # -------------------------------------------------------------

            # 수량 증가(+) 버튼 클릭
            plus_btn = page.locator('div.kpds_j1jks26.kpds_j1jks28').first
            plus_btn.click(force=True)
            page.wait_for_timeout(1000)

            # 증가 후 수량 확인 및 assert 검증
            count_after_plus = int(re.sub(r'[^0-9]', '', count_elem.inner_text()))
            print(f"   - 수량 증가 후: {count_after_plus}개")
            assert count_after_plus == initial_count + 1, f"수량 증가 실패: 기대값 {initial_count + 1}, 현재값 {count_after_plus}"
            
            
            # -------------------------------------------------------------
            # 4. 수량 감소(-) 테스트
            # -------------------------------------------------------------
            minus_btn = page.locator('div.kpds_j1jks26.kpds_j1jks27').first
            minus_btn.click(force=True)
            page.wait_for_timeout(1000)

            # 감소 후 수량 확인 및 assert 검증
            count_after_minus = int(re.sub(r'[^0-9]', '', count_elem.inner_text()))
            print(f"   - 수량 감소 후: {count_after_minus}개")
            assert count_after_minus == count_after_plus - 1, f"수량 감소 실패: 기대값 {count_after_plus - 1}, 현재값 {count_after_minus}"

            print("   ✅ CART_02 성공: 장바구니 수량 증가 및 감소 확인 완료!")

            # =============================================================
            # [CART_03] 장바구니 상품 선택 해제 시 결제 예정 금액 0원 반영
            # =============================================================
            print("\n3. [CART_03] 전체 선택 해제 시 결제 금액 0원 변경 테스트")
            
            # [전체 선택] 체크박스 또는 버튼 클릭하여 해제
            select_all_btn = page.locator('label:has-text("전체선택"), input[type="checkbox"]').first
            select_all_btn.click(force=True)
            page.wait_for_timeout(1000)

            # 초기 단가/결제 금액 텍스트 추출
            total_price_elem = page.locator('div.css-zorl92.ebe7z6d0').last # 결제예정금액
            initial_price_text = total_price_elem.inner_text() # 수량 변경 전 금액
            initial_price = int(re.sub(r'[^0-9]', '', initial_price_text))

            # 결제 금액 0원 변경 확인
            #zero_price_text = total_price_elem.inner_text()
            #zero_price = int(re.sub(r'[^0-9]', '', zero_price_text))

            print(f"   - 전체 선택 해제 후 결제 금액: {initial_price}원")
            assert initial_price == 0, f"CART_03 실패: 선택 해제 후 금액이 0원이 아님 ({initial_price}원)"
            print("   ✅ CART_03 성공: 전체 선택 해제 시 결제 예정 금액 0원 확인 완료!")

            # =============================================================
            # [CART_04] 단일 상품 삭제 (X 버튼 클릭 시 상품 삭제)
            # =============================================================
            print("\n3. [CART_04] 개별 체크박스 해제 시 전체선택 수량 차감 테스트")

            select_all_btn.click()

            # 1. 전체선택 수량 텍스트 요소 타겟팅 (label 내 p 태그)
            select_all_p = page.locator('label', has_text="전체선택").locator('p').first

            # 2. 클릭 전 수량 파싱
            count_text = select_all_p.inner_text()
            if '/' in count_text:
                # '/' 바로 앞의 숫자만 파싱
                initial_count = int(re.search(r'(\d+)\s*/', count_text).group(1))
            else:
                # 예외 상황용 (숫자만 있는 경우)
                initial_count = int(re.sub(r'[^0-9]', '', count_text))

            print(f"   - 선택 해제 전 전체선택 수량: {initial_count}개")

            # 3. 첫 번째 상품 카드 내의 체크박스(또는 라벨) 클릭하여 선택 해제
            first_item_checkbox = page.locator('div.css-1tqud6q.eavuhc61').first
            first_item_checkbox.locator('label').first.click(force=True)
            page.wait_for_timeout(1000)

            # 4. 클릭 후 전체선택 수량 재파싱
            updated_text = select_all_p.inner_text()
            if '/' in updated_text:
                updated_count = int(re.search(r'(\d+)\s*/', updated_text).group(1))
            else:
                updated_count = int(re.sub(r'[^0-9]', '', updated_text))

            print(f"   - 선택 해제 후 전체선택 수량: {updated_count}개")

            # 5. 수량이 정확히 1개 줄어들었는지 검증 (Assertion)
            assert updated_count == initial_count - 1, (
                f"CART_04 실패: 수량이 줄어들지 않았습니다. (기존: {initial_count}, 변경: {updated_count})"
            )
            print("   ✅ CART_04 성공: 개별 체크박스 해제 시 전체선택 수량 1 차감 확인 완료!")
