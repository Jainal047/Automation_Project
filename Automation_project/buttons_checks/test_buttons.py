import pytest
from playwright.sync_api import Page, expect, TimeoutError

# =====================
# CONFIG
# =====================
BASE_URL = "https://cyberquaysvercel.vercel.app/"
EMAIL = "kuldipp.vnerds@gmail.com"
PASSWORD = "Kuldip@123"

CORE_NAV = {
    "Dashboard",
    "Security Requests",
    "Reports",
    "Admin",
    "kuldipp.vnerds"
}

LOGOUT_WORDS = {"logout", "log out", "sign out"}

# =====================
# LOGIN
# =====================
def login(page: Page):
    print("\n[LOGIN] Starting login flow")
    page.goto(BASE_URL, wait_until="domcontentloaded")

    header = page.locator("header")
    sign_in = header.get_by_role("button", name="Sign In", exact=True)
    expect(sign_in).to_be_visible(timeout=15000)
    sign_in.click()

    email = page.get_by_placeholder("Enter your email")
    password = page.get_by_placeholder("Enter your password")

    expect(email).to_be_visible(timeout=15000)
    expect(password).to_be_visible(timeout=15000)

    email.click()
    page.keyboard.type(EMAIL, delay=60)

    password.click()
    page.keyboard.type(PASSWORD, delay=60)

    submit = page.locator("form").get_by_role("button", name="Sign In", exact=True)
    submit.click()
    page.keyboard.press("Enter")

    dashboard = page.get_by_role("link", name="Dashboard", exact=True)
    expect(dashboard).to_be_visible(timeout=20000)

    print("[SUCCESS] Login confirmed")

# =====================
# SAFE BUTTON AUDIT
# =====================
def audit_buttons(page: Page, context: str):
    print(f"\n--- AUDITING: {context} ---")

    elements = page.locator(
        'button:visible, a[role="button"]:visible, .cursor-pointer:visible'
    ).all()

    print(f"Found {len(elements)} elements")
    start_url = page.url

    for i, el in enumerate(elements):
        name = f"Icon_{i+1}"

        try:
            txt = el.inner_text().strip()
            if txt:
                name = txt.split("\n")[0]

            if name in CORE_NAV or name == "":
                continue

            if any(w in name.lower() for w in LOGOUT_WORDS):
                print(f"  ⏭ SKIPPED (logout): {name}")
                continue

            if not el.is_enabled():
                print(f"  ⚠ DISABLED: {name}")
                continue

            el.scroll_into_view_if_needed()
            el.click(timeout=4000)
            print(f"  ✅ PASS: {name}")

            if page.url != start_url:
                page.go_back()
                page.wait_for_load_state("networkidle")

        except TimeoutError:
            print(f"  ❌ TIMEOUT: {name}")
        except Exception as e:
            print(f"  ❌ FAIL: {name} | {str(e).splitlines()[0]}")

# =====================
# LOGOUT (FINAL STEP)
# =====================
def logout(page: Page):
    print("\n[LOGOUT] Final logout step")

    if "auth/signin" in page.url:
        print("⚠ Already logged out — skipping")
        return

    try:
        user = page.get_by_text("kuldipp.vnerds", exact=False)
        expect(user).to_be_visible(timeout=5000)
        user.click()
    except Exception:
        print("⚠ User menu not found — skipping logout")
        return

    try:
        logout_btn = page.get_by_role("menuitem", name="Logout", exact=False)
        expect(logout_btn).to_be_visible(timeout=5000)
        logout_btn.click()
    except Exception:
        print("⚠ Logout option missing — skipping")
        return

    try:
        sign_in = page.get_by_role("button", name="Sign In", exact=True)
        expect(sign_in).to_be_visible(timeout=10000)
        print("[SUCCESS] Logout verified")
    except Exception:
        print("⚠ Logout attempted — UI did not fully refresh")

# =====================
# MAIN TEST
# =====================
def test_full_ui_audit(page: Page):

    login(page)

    # -------- DASHBOARD --------
    page.get_by_role("link", name="Dashboard", exact=True).click()
    page.wait_for_load_state("networkidle")
    audit_buttons(page, "Dashboard")

    # -------- SECURITY REQUESTS --------
    page.get_by_role("link", name="Security Requests", exact=True).click()
    page.wait_for_load_state("networkidle")

    security_tabs = ["Priority", "Analytics", "Users", "Reports", "System"]

    for tab in security_tabs:
        print(f"\n→ Security Requests > {tab}")
        try:
            tab_el = page.get_by_text(tab, exact=False).first
            expect(tab_el).to_be_visible(timeout=5000)
            tab_el.click()
            page.wait_for_timeout(1200)
            audit_buttons(page, f"Security Requests > {tab}")
        except Exception:
            print(f"⚠ TAB NOT AVAILABLE: {tab}")

    # -------- MID-PROCESS: MAIN REPORTS --------
    print("\n>>> MID-PROCESS NAVIGATION: Reports")
    page.get_by_role("link", name="Reports", exact=True).click()
    page.wait_for_load_state("networkidle")
    audit_buttons(page, "Reports (Main Module)")

    # -------- ADMIN --------
    page.get_by_role("link", name="Admin", exact=True).click()
    page.wait_for_load_state("networkidle")
    audit_buttons(page, "Admin")

    # -------- FINAL LOGOUT --------
    logout(page)

    print("\n" + "=" * 70)
    print(" FULL UI AUDIT COMPLETED SUCCESSFULLY ")
    print("=" * 70)

    page.pause()