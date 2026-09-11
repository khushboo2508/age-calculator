import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta


st.title("🎂 Age Calculator")
st.write("Calculate your exact age and find out when your next birthday is.")


dob = st.date_input(
    "Enter your Date of Birth",
    min_value=date(1900, 1, 1),
    max_value=date.today()
)


if st.button("Calculate Age"):
    today = date.today()

    age = relativedelta(today, dob)

    next_birthday = dob.replace(year=today.year)

    if next_birthday <= today:
        next_birthday = dob.replace(year=today.year + 1)

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
    st.write("🎉 **Next Birthday:**", next_birthday.strftime("%d-%m-%Y"))
    st.write("⏳ **Days Remaining:**", days_remaining)