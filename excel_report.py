from openpyxl import Workbook


def create_excel_report(expenses, file_path):

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Expense Report"

    # Headers
    headers = [
        "ID",
        "Date",
        "Category",
        "Description",
        "Amount",
        "Payment Method",
        "Notes"
    ]

    sheet.append(headers)

    # Expense data
    for expense in expenses:
        sheet.append(expense)

    # Summary
    total_expenses = sum(float(expense[4]) for expense in expenses)
    number_of_expenses = len(expenses)

    if number_of_expenses > 0:
        average_expense = total_expenses / number_of_expenses
    else:
        average_expense = 0

    sheet.append([])
    sheet.append(["Summary"])
    sheet.append(["Total Expenses", total_expenses])
    sheet.append(["Number of Expenses", number_of_expenses])
    sheet.append(["Average Expense", average_expense])

    workbook.save(file_path)