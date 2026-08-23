from playwright.sync_api import sync_playwright

def run_login_tests():
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
            # =============================================================
            # [LOG_01] 미입력 상태 로그인 시도 시 예외 처리
            # =============================================================
            print("\n1. [LOG_01] 미입력 상태 로그인 시도 테스트")
            print("1. 컬리 로그인 페이지 진입...")
            page.goto("https://www.kurly.com/member/login")
            
            # 2. 네트워크 및 화면 로딩 완벽 대기
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(3000) # 화면이 완전히 그려질 때까지 3초 여유 대기

            print("2. 버튼 존재 여부 탐색 중...")

            # 아이디/비밀번호 미입력 상태에서 로그인 버튼 클릭
            login_btn = page.locator('button[type="submit"]')
            login_btn.first.click(force=True)
            page.wait_for_timeout(1000)

            # Alert/Modal 팝업 검증 (팝업 모달 또는 alert 다이얼로그)
            # 컬리 모달 셀렉터 또는 role="dialog" 활용
            alert_modal = page.locator('[role="dialog"]').first
            alert_modal.wait_for(state="visible", timeout=5000) # 팝업이 뜰 때까지 최대 5초 대기
            
            modal_text = alert_modal.inner_text()
            print(f"   - 노출된 팝업 문구: '{modal_text.replace(chr(10), ' ')}'")
            assert "로그인에 실패하였습니다" in modal_text or "고객센터" in modal_text, "LOG_01 실패: 예외 팝업 텍스트 불일치"
            print("   ✅ LOG_01 성공: 미입력 로그인 예외 처리 팝업 검증 완료!")

            # 팝업 닫기 (다음 테스트 진행을 위해)
            # 팝업 내부에서 '확인' 글자를 갖고 있는 button 태그 찾기
            confirm_btn = alert_modal.locator('button:has-text("확인")')
            confirm_btn.click(force=True)

            # =============================================================
            # [LOG_02] 잘못된 아이디/비밀번호 입력 예외 처리
            # =============================================================
            print("\n2. [LOG_02] 잘못된 아이디/비밀번호 입력 테스트")
            # 팝업 닫기 (이전 팝업이 있다면)
            #if alert_modal.is_visible():
            #    page.click('button:has-text("확인")')

            # 존재하지 않는 계정 정보 입력
            page.get_by_placeholder("아이디를 입력해주세요").fill('wrong_user')
            page.get_by_placeholder("비밀번호를 입력해주세요").fill('Wrong123!')
            page.click('button[type="submit"]')
            page.wait_for_timeout(2000)

            # 안내 팝업 검증
            dialog_modal = page.locator('[role="dialog"]')
            if dialog_modal.is_visible():
                assert "확인" in dialog_modal.inner_text(), "잘못된 계정 로그인 팝업 미노출"
                print("   ✅ LOG_02 성공: 계정 오류 예외 안내 팝업 확인 완료")

            # =============================================================
            # [LOG_03] 비로그인 상태에서 회원 전용 기능 접근 시 예외 처리
            # =============================================================
            print("\n3. [LOG_03] 비로그인 상태 회원 전용 기능(찜하기) 접근 테스트")
            page.goto("https://www.kurly.com")
            page.wait_for_load_state("networkidle")

            # 첫 번째 상품의 찜하기(하트) 버튼 클릭 시도
            like_button = page.locator('button:has(path[d^="M12.68"])').first.click()
            if like_button.is_visible():
                like_button.click()
                page.wait_for_timeout(2000)
                
                # 로그인 유도 팝업 확인
                auth_popup = page.locator('div', has_text="로그인하셔야").first()

                auth_popup.wait_for(state="visible", timeout=5000)

                if auth_popup.is_visible():
                    assert "로그인하셔야" in auth_popup.inner_text(), "로그인 유도 팝업 미노출"
                    print("   ✅ LOG_03 성공: 비로그인 찜하기 시 로그인 유도 팝업 확인 완료")
                

            print("\n🎉 [LOG_01 ~ LOG_03] 로그인 테스트 전체 완료!")

        except Exception as e:
            print(f"\n❌ 테스트 수행 중 에러 발생: {e}")

        finally:
            page.wait_for_timeout(2000)
            browser.close()

if __name__ == "__main__":
    run_login_tests()