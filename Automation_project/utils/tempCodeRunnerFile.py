from pathlib import Path
import openpyxl

def read_login_test_data():
    project_root = Path(__file__).resolve().parent.parent
    excel_path = project_root / "utils" / "test_cases.xlsx"

    workbook = openpyxl.load_workbook(excel_path)
    sheet = workbook.active

    data = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        email, password, expected = row[2], row[3], row[4]

        # Default expected = error if empty
        if expected is None or str(expected).strip() == "":
            expected = "error"

        data.append({
            "email": "" if email is None else str(email),
            "password": "" if password is None else str(password),
            "expected": expected.lower()
        })

    return data
