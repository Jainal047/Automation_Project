import pytest
from playwright.sync_api import Page, expect

def login(page: Page):
    """Handles homepage → login → dashboard with corrected URLs"""
    print("Opening homepage...")
    page.goto("https://cyberquaysvercel.vercel.app/", wait_until="networkidle")

    # --- CLICK TOP NAV SIGN IN ---
    # Attempting to find the Sign In button in the header
    sign_in_nav = page.get_by_role("button", name="Sign In", exact=True)
    
    # If the button is visible, click it. If we are already on the signin page, skip.
    if sign_in_nav.is_visible():
        sign_in_nav.click()

    # --- WAIT FOR THE CORRECT LOGIN URL ---
    # Fixed: Your site uses /auth/signin, not /login
    print("Waiting for sign-in page...")
    page.wait_for_url("**/auth/signin**", timeout=15000)

    # --- FILL CREDENTIALS ---
    print("Filling credentials...")
    # Using placeholders as seen in your 'Welcome Back' image
    page.get_by_placeholder("Enter your email").fill("kuldipp.vnerds@gmail.com")
    page.get_by_placeholder("Enter your password").fill("Kuldip@123")

    # --- SUBMIT LOGIN ---
    # Clicking the 'Sign In' button on the login card
    login_btn = page.locator('button:has-text("Sign In")').last
    expect(login_btn).to_be_enabled(timeout=10000)
    login_btn.click()

    # --- WAIT FOR DASHBOARD ---
    print("Login submitted. Waiting for dashboard...")
    page.wait_for_load_state("networkidle")
    # Wait for the specific Dashboard link to ensure we are truly logged in
    page.get_by_role("link", name="Dashboard").wait_for(state="visible", timeout=15000)


def audit_clickables(page: Page, skip_names: list):
    """Clicks and validates all visible actionable elements"""
    items = page.locator(
        'button:visible, a[role="button"]:visible, .cursor-pointer:visible'
    ).all()

    for idx, item in enumerate(items):
        try:
            name = item.inner_text().strip().split('\n')[0] or f"Icon_{idx+1}"
        except:
            name = f"Element_{idx+1}"

        # Skip navigation and user profile to stay on the current page
        if name in skip_names or "kuldipp.vnerds" in name.lower():
            continue

        print(f"   Checking: {name}")

        try:
            expect(item).to_be_visible(timeout=2000)
            if not item.is_enabled():
                print(f"      ⚠ DISABLED")
                continue

            item.scroll_into_view_if_needed()
            item.click(timeout=3000)
            print(f"      ✅ PASS")
            
            # If the click caused a navigation, go back to keep testing buttons
            if page.url.endswith("/auth/signin") == False and any(mod in page.url for mod in ["Dashboard", "Reports", "Admin"]):
                pass # Still on a main module
            else:
                page.go_back()
                page.wait_for_load_state("networkidle")

        except Exception as e:
            print(f"      ❌ FAIL -> {str(e).split('=')[0].strip()}")


def test_complete_ui_audit(page: Page):
    # --- 1. LOGIN FLOW ---
    login(page)

    # --- 2. MODULES TO AUDIT ---
    modules = ["Dashboard", "Security Requests", "Reports", "Admin"]

    for module in modules:
        print(f"\n>>> AUDITING MODULE: {module}")
        try:
            page.get_by_role("link", name=module, exact=True).click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)
            
            audit_clickables(page, skip_names=modules)
        except Exception:
            print(f"❌ Could not navigate to {module}")
            continue

    print("\n[AUDIT COMPLETE]")
    page.pause()


    (pytest.main(["-s", "test_complete_ui_audit.py"]))
    
    # pytest -s test_complete_ui_audit.py -k "test_complete_ui_audit"   
    # pytest -s test_complete_ui_audit.py -k "test_complete_ui_audit" --headed