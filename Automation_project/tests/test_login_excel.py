import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils.excel_reader import read_login_test_data

URL = "https://cyberquaysvercel.vercel.app/"

@pytest.mark.parametrize("data", read_login_test_data())
def test_login_excel(data):
    # 'detach' keeps the browser open for manual inspection
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    driver.get(URL)

    try:
        # Open login modal
        wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Sign In')]"))
        ).click()

        # Input Email
        email_field = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='email' or @type='text']"))
        )
        email_field.clear()
        email_field.send_keys(data["email"])

        # Input Password
        password_field = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
        )
        password_field.clear()
        password_field.send_keys(data["password"])

        # Click Submit
        wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        ).click()

        # -------- LOGIC FOR SUCCESS/ERROR --------
        try:
            # Check if Dashboard text exists on page
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Dashboard')]"))
            )
            actual_result = "success"
        except TimeoutException:
            actual_result = "error"

        # Determine FINAL STATUS based on Excel 'expected' column
        if actual_result == data["expected"]:
            final_status = "PASS"
            page_status = "Dashboard Page Reached"
        else:
            final_status = "FAIL"
            page_status = "Dashboard Page Not Reached"

        # -------- PRINT OUTPUT --------
        print(f"\n--------------------------------------------------")
        print(f"EMAIL           : {data['email']}")
        print(f"PAGE STATUS     : {page_status}")
        print(f"FINAL STATUS    : {final_status}")
        print("--------------------------------------------------")

    except Exception as e:
        print(f"\nError executing test for {data['email']}: {e}")