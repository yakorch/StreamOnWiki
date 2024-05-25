import datetime


def date_range(start_date: str, end_date: str):
    # Convert start_date and end_date from strings to date objects
    start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

    for n in range(int((end - start).days) + 1):
        yield start + datetime.timedelta(n)
