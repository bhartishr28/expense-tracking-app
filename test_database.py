#from database import get_connection
# from database import get_categories
#
# categories = get_categories()
#
# for category in categories:
#     print(category)

# from database import get_payment_methods
#
# payment_methods = get_payment_methods()
#
# for payment_method in payment_methods:
#     print(payment_method)

#

from database import get_expenses

expenses = get_expenses()
for expense in expenses:
    print(expense)
#
# from database import update_expenses
#
# update_expenses(
#     5,
#     '2026-09-29',
#     1,
#     'Updated Lunch',
#     300.00,
#     2,
#     'Updated note'
# )

# print("Expense updated successfully!")
#
# from database import delete_expenses
# delete_expenses(5)
# print(f"Expense deleted successfully!")




