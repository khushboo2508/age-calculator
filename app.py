import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
import calendar


st.title("🎂 Age Calculator")
st.write("Calculate your exact age and find out when your next birthday is.")


# Date of Birth
today = date.today()

st.subheader("Enter your Date of Birth")

col1, col2, col3 = st.columns(3)

with col1:
    day = st.selectbox(
        "Day",
        range(1, 32),
        index=0
    )

with col2:
    month = st.selectbox(
        "Month",
        range(1, 13),
        format_func=lambda x: calendar.month_name[x]
    )

with col3:
    year = st.selectbox(
        "Year",
        range(1900, today.year + 1),
        index=today.year - 1900
    )


# Handle invalid dates such as 31 February
max_day = calendar.monthrange(year, month)[1]

if day > max_day:
    st.warning(
        f"{calendar.month_name[month]} {year} has only {max_day} days. "
        f"Please select a valid day."
    )
else:
    dob = date(year, month, day)

    if dob > today:
        st.error("Date of Birth cannot be in the future.")

    else:
        if st.button("Calculate Age"):

            age = relativedelta(today, dob)

            # Next birthday
            try:
                next_birthday = dob.replace(year=today.year)
            except ValueError:
                # For February 29
                next_birthday = date(today.year, 2, 28)

            if next_birthday <= today:
                try:
                    next_birthday = dob.replace(year=today.year + 1)
                except ValueError:
                    next_birthday = date(today.year + 1, 2, 28)

            days_remaining = (next_birthday - today).days

            st.subheader("Your Result")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Years", age.years)

            with col2:
                st.metric("Months", age.months)

            with col3:
                st.metric("Days", age.days)

            st.write("📅 **Day of Birth:**", dob.strftime("%A"))
            st.write(
                "🎉 **Next Birthday:**",
                next_birthday.strftime("%d-%m-%Y")
            )
            st.write("⏳ **Days Remaining:**", days_remaining)