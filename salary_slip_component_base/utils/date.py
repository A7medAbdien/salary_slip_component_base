from frappe.utils import get_last_day, add_months, getdate

def get_last_dates_between(start_date, end_date):
    """
    Returns a list of the last dates of each month between two dates.

    Args:
        start_date (str or datetime): The start date.
        end_date (str or datetime): The end date.

    Returns:
        list: A list of strings representing the last dates of each month.
    """
    start_date = getdate(start_date)
    end_date = getdate(end_date)
    last_dates = []

    current_date = start_date.replace(day=1)

    while current_date <= end_date:
        last_day = get_last_day(current_date)
        last_dates.append(last_day)

        # Move to the first day of the next month
        current_date = add_months(current_date, 1)

    return last_dates
