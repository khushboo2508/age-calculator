from datetime import datetime
from dateutil.relativedelta import relativedelta


def calculate_age(birth_date, today):
    """Calculate exact age in years, months, and days."""
    age = relativedelta(today, birth_date)
    return age


def get_next_birthday(birth_date, today):
    """Calculate the next birthday and remaining days."""
    next_birthday = birth_date.replace(year=today.year)

    if next_birthday <= today:
        next_birthday = birth_date.replace(year=today.year + 1)

    days_remaining = (next_birthday - today).days

    return next_birthday, days_remaining


def display_result(dob, birth_date, age, next_birthday, days_remaining):
    """Display the age calculator result."""
    print("\n========================================")
    print("           AGE CALCULATOR")
    print("========================================")

    print("\nYour Date of Birth:", dob)
    print("Day of Birth:", birth_date.strftime("%A"))

    print("\nYour Age:")
    print(
        age.years,
        "Years,",
        age.months,
        "Months,",
        age.days,
        "Days"
    )

    print("\nNext Birthday:", next_birthday.strftime("%d-%m-%Y"))
    print("Days Remaining:", days_remaining, "days")

    print("\n========================================")


while True:
    dob = input("Enter your date of birth (DD-MM-YYYY): ")

    try:
        birth_date = datetime.strptime(dob, "%d-%m-%Y").date()
        today = datetime.today().date()

        if birth_date > today:
            print("Invalid Date of Birth: Future date is not allowed.")
        else:
            age = calculate_age(birth_date, today)

            next_birthday, days_remaining = get_next_birthday(
                birth_date, today
            )

            display_result(
                dob,
                birth_date,
                age,
                next_birthday,
                days_remaining
            )

            break

    except ValueError:
        print("Invalid Date. Please enter DOB in DD-MM-YYYY format.")