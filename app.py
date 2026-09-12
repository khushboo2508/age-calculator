import streamlit as st
from datetime import date, datetime, time, timezone
from dateutil.relativedelta import relativedelta
import calendar

import swisseph as swe
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="Age Calculator",
    page_icon="🎂",
    layout="wide"
)


# =========================================================
# CONSTANTS
# =========================================================

SIGNS = [
    "Aries (Mesha)",
    "Taurus (Vrishabha)",
    "Gemini (Mithuna)",
    "Cancer (Karka)",
    "Leo (Simha)",
    "Virgo (Kanya)",
    "Libra (Tula)",
    "Scorpio (Vrishchika)",
    "Sagittarius (Dhanu)",
    "Capricorn (Makara)",
    "Aquarius (Kumbha)",
    "Pisces (Meena)"
]

NAKSHATRAS = [
    ("Ashwini", "Ketu"),
    ("Bharani", "Venus"),
    ("Krittika", "Sun"),
    ("Rohini", "Moon"),
    ("Mrigashira", "Mars"),
    ("Ardra", "Rahu"),
    ("Punarvasu", "Jupiter"),
    ("Pushya", "Saturn"),
    ("Ashlesha", "Mercury"),
    ("Magha", "Ketu"),
    ("Purva Phalguni", "Venus"),
    ("Uttara Phalguni", "Sun"),
    ("Hasta", "Moon"),
    ("Chitra", "Mars"),
    ("Swati", "Rahu"),
    ("Vishakha", "Jupiter"),
    ("Anuradha", "Saturn"),
    ("Jyeshtha", "Mercury"),
    ("Mula", "Ketu"),
    ("Purva Ashadha", "Venus"),
    ("Uttara Ashadha", "Sun"),
    ("Shravana", "Moon"),
    ("Dhanishta", "Mars"),
    ("Shatabhisha", "Rahu"),
    ("Purva Bhadrapada", "Jupiter"),
    ("Uttara Bhadrapada", "Saturn"),
    ("Revati", "Mercury")
]

DASHA_ORDER = [
    "Ketu",
    "Venus",
    "Sun",
    "Moon",
    "Mars",
    "Rahu",
    "Jupiter",
    "Saturn",
    "Mercury"
]

DASHA_YEARS = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17
}

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE
}


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_sign(longitude):
    index = int(longitude // 30) % 12
    return SIGNS[index]


def get_degree_in_sign(longitude):
    return longitude % 30


def format_degree(degree):
    d = int(degree)

    minutes_float = (degree - d) * 60
    m = int(minutes_float)

    s = int(round((minutes_float - m) * 60))

    if s == 60:
        s = 0
        m += 1

    if m == 60:
        m = 0
        d += 1

    return f"{d}° {m}' {s}\""


def get_nakshatra(longitude):
    nakshatra_size = 360 / 27
    pada_size = nakshatra_size / 4

    index = int(longitude / nakshatra_size)

    if index >= 27:
        index = 26

    name, lord = NAKSHATRAS[index]

    position = longitude - (index * nakshatra_size)

    pada = int(position / pada_size) + 1

    return name, pada, lord


def geocode_location(location_text):

    geolocator = Nominatim(
        user_agent="age_calculator_app"
    )

    location = geolocator.geocode(
        location_text,
        timeout=10
    )

    if location is None:
        return None

    latitude = location.latitude
    longitude = location.longitude

    timezone_finder = TimezoneFinder()

    timezone_name = timezone_finder.timezone_at(
        lat=latitude,
        lng=longitude
    )

    if timezone_name is None:
        timezone_name = "UTC"

    return latitude, longitude, timezone_name


def calculate_julian_day(
    birth_date,
    birth_time,
    timezone_name
):

    local_datetime = datetime.combine(
        birth_date,
        birth_time
    )

    local_zone = ZoneInfo(timezone_name)

    local_datetime = local_datetime.replace(
        tzinfo=local_zone
    )

    utc_datetime = local_datetime.astimezone(
        timezone.utc
    )

    hour_decimal = (
        utc_datetime.hour
        + utc_datetime.minute / 60
        + utc_datetime.second / 3600
    )

    jd_ut = swe.julday(
        utc_datetime.year,
        utc_datetime.month,
        utc_datetime.day,
        hour_decimal,
        swe.GREG_CAL
    )

    return jd_ut


def calculate_planets(jd_ut):

    # Lahiri ayanamsha
    swe.set_sid_mode(
        swe.SIDM_LAHIRI
    )

    flags = (
        swe.FLG_SWIEPH
        | swe.FLG_SIDEREAL
        | swe.FLG_SPEED
    )

    results = {}

    for planet_name, planet_id in PLANETS.items():

        position, _ = swe.calc_ut(
            jd_ut,
            planet_id,
            flags
        )

        longitude = position[0]
        speed = position[3]

        sign = get_sign(longitude)

        degree = get_degree_in_sign(
            longitude
        )

        nakshatra, pada, nakshatra_lord = (
            get_nakshatra(longitude)
        )

        results[planet_name] = {
            "longitude": longitude,
            "degree": degree,
            "sign": sign,
            "nakshatra": nakshatra,
            "pada": pada,
            "nakshatra_lord": nakshatra_lord,
            "retrograde": speed < 0
        }

    # Ketu is opposite Rahu
    rahu_longitude = results["Rahu"]["longitude"]

    ketu_longitude = (
        rahu_longitude + 180
    ) % 360

    ketu_sign = get_sign(
        ketu_longitude
    )

    ketu_degree = get_degree_in_sign(
        ketu_longitude
    )

    ketu_nakshatra, ketu_pada, ketu_lord = (
        get_nakshatra(ketu_longitude)
    )

    results["Ketu"] = {
        "longitude": ketu_longitude,
        "degree": ketu_degree,
        "sign": ketu_sign,
        "nakshatra": ketu_nakshatra,
        "pada": ketu_pada,
        "nakshatra_lord": ketu_lord,
        "retrograde": True
    }

    return results


def calculate_ascendant(
    jd_ut,
    latitude,
    longitude
):

    swe.set_sid_mode(
        swe.SIDM_LAHIRI
    )

    cusps, ascmc = swe.houses_ex(
        jd_ut,
        latitude,
        longitude,
        b"P",
        swe.FLG_SIDEREAL
    )

    ascendant = ascmc[0]

    return ascendant, cusps


def get_whole_sign_house(
    planet_longitude,
    ascendant_longitude
):

    ascendant_sign = int(
        ascendant_longitude // 30
    )

    planet_sign = int(
        planet_longitude // 30
    )

    house = (
        planet_sign
        - ascendant_sign
    ) % 12 + 1

    return house


def calculate_dasha(
    birth_date,
    moon_longitude
):

    nakshatra_size = 360 / 27

    nakshatra_index = int(
        moon_longitude / nakshatra_size
    )

    birth_lord = NAKSHATRAS[
        nakshatra_index
    ][1]

    nakshatra_start = (
        nakshatra_index
        * nakshatra_size
    )

    travelled = (
        moon_longitude
        - nakshatra_start
    )

    fraction_completed = (
        travelled / nakshatra_size
    )

    fraction_remaining = (
        1 - fraction_completed
    )

    first_duration = (
        DASHA_YEARS[birth_lord]
        * fraction_remaining
    )

    birth_datetime = datetime.combine(
        birth_date,
        time(0, 0)
    )

    timeline = []

    start_index = DASHA_ORDER.index(
        birth_lord
    )

    current_start = birth_datetime

    # Create a sufficiently long timeline
    for i in range(15):

        lord = DASHA_ORDER[
            (start_index + i) % 9
        ]

        if i == 0:
            duration_years = first_duration
        else:
            duration_years = DASHA_YEARS[lord]

        duration_seconds = (
            duration_years
            * 365.2425
            * 24
            * 60
            * 60
        )

        current_end = datetime.fromtimestamp(
            current_start.timestamp()
            + duration_seconds
        )

        timeline.append({
            "lord": lord,
            "start": current_start,
            "end": current_end
        })

        current_start = current_end

    now = datetime.now()

    current_mahadasha = None

    for dasha in timeline:

        if (
            dasha["start"]
            <= now
            <= dasha["end"]
        ):
            current_mahadasha = dasha
            break

    current_antardasha = None

    if current_mahadasha:

        maha_lord = (
            current_mahadasha["lord"]
        )

        maha_years = DASHA_YEARS[
            maha_lord
        ]

        maha_index = DASHA_ORDER.index(
            maha_lord
        )

        ant_start = (
            current_mahadasha["start"]
        )

        for j in range(9):

            ant_lord = DASHA_ORDER[
                (maha_index + j) % 9
            ]

            ant_years = (
                maha_years
                * DASHA_YEARS[ant_lord]
                / 120
            )

            ant_seconds = (
                ant_years
                * 365.2425
                * 24
                * 60
                * 60
            )

            ant_end = datetime.fromtimestamp(
                ant_start.timestamp()
                + ant_seconds
            )

            if (
                ant_start
                <= now
                <= ant_end
            ):
                current_antardasha = {
                    "lord": ant_lord,
                    "start": ant_start,
                    "end": ant_end
                }
                break

            ant_start = ant_end

    return (
        birth_lord,
        timeline,
        current_mahadasha,
        current_antardasha
    )


def find_yoga_indicators(planets):

    yogas = []

    moon_sign = SIGNS.index(
        planets["Moon"]["sign"]
    )

    jupiter_sign = SIGNS.index(
        planets["Jupiter"]["sign"]
    )

    distance = (
        jupiter_sign
        - moon_sign
    ) % 12

    if distance in [0, 3, 6, 9]:
        yogas.append(
            "Gajakesari Yoga indicator"
        )

    if (
        planets["Sun"]["sign"]
        == planets["Mercury"]["sign"]
    ):
        yogas.append(
            "Budha-Aditya Yoga indicator"
        )

    if (
        planets["Moon"]["sign"]
        == planets["Mars"]["sign"]
    ):
        yogas.append(
            "Chandra-Mangal Yoga indicator"
        )

    if (
        planets["Sun"]["sign"]
        == planets["Jupiter"]["sign"]
    ):
        yogas.append(
            "Sun-Jupiter conjunction indicator"
        )

    if not yogas:
        yogas.append(
            "No basic yoga indicator detected."
        )

    return yogas


# =========================================================
# MAIN AGE CALCULATOR
# =========================================================

st.title("🎂 Age Calculator")

st.write(
    "Calculate your exact age and find out when "
    "your next birthday is."
)


st.subheader("📅 Enter your Date of Birth")

col1, col2, col3 = st.columns(3)

today = date.today()
current_year = today.year

with col1:

    day = st.selectbox(
        "Day",
        range(1, 32)
    )

with col2:

    month = st.selectbox(
        "Month",
        range(1, 13),
        format_func=lambda x:
        calendar.month_name[x]
    )

with col3:

    year = st.selectbox(
        "Year",
        range(
            1900,
            current_year + 1
        ),
        index=current_year - 1900
    )


# =========================================================
# VALID DATE
# =========================================================

try:

    dob = date(
        year,
        month,
        day
    )

    valid_dob = dob <= today

except ValueError:

    valid_dob = False
    dob = None


if not valid_dob:

    st.warning(
        "Please select a valid date."
    )


# =========================================================
# CALCULATE AGE BUTTON
# =========================================================

if st.button(
    "Calculate Age",
    type="primary"
):

    if not valid_dob:

        st.error(
            "Please enter a valid Date of Birth."
        )

    else:

        age = relativedelta(
            today,
            dob
        )

        # Next birthday
        try:

            next_birthday = dob.replace(
                year=today.year
            )

        except ValueError:

            # February 29
            next_birthday = date(
                today.year,
                2,
                28
            )

        if next_birthday <= today:

            try:

                next_birthday = dob.replace(
                    year=today.year + 1
                )

            except ValueError:

                next_birthday = date(
                    today.year + 1,
                    2,
                    28
                )

        days_remaining = (
            next_birthday - today
        ).days

        # =================================================
        # AGE RESULT
        # =================================================

        st.subheader("🎯 Your Result")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Years",
                age.years
            )

        with col2:

            st.metric(
                "Months",
                age.months
            )

        with col3:

            st.metric(
                "Days",
                age.days
            )

        st.write(
            "📅 **Day of Birth:**",
            dob.strftime("%A")
        )

        st.write(
            "🎉 **Next Birthday:**",
            next_birthday.strftime(
                "%d-%m-%Y"
            )
        )

        st.write(
            "⏳ **Days Remaining:**",
            days_remaining
        )

        st.write(
            "🎈 **Next Birthday Day:**",
            next_birthday.strftime("%A")
        )


# =========================================================
# OPTIONAL BIRTH CHART
# =========================================================

st.divider()

with st.expander(
    "✨ Explore Your Birth Chart (Optional)"
):

    st.info(
        "This section is optional. "
        "You can use the Age Calculator without "
        "entering your birth time or location."
    )

    st.write(
        "For birth-chart calculations, please provide "
        "your exact birth time and birth location."
    )

    col1, col2 = st.columns(2)

    with col1:

        birth_time = st.time_input(
            "🕐 Exact Birth Time",
            value=time(12, 0)
        )

    with col2:

        birth_location = st.text_input(
            "📍 Birth Location",
            placeholder="Example: Delhi, India"
        )

    st.caption(
        "Enter the city/place where you were born "
        "as accurately as possible."
    )

    generate_chart = st.button(
        "🔮 Generate Birth Chart",
        type="primary"
    )

    # =====================================================
    # GENERATE BIRTH CHART
    # =====================================================

    if generate_chart:

        if not valid_dob:

            st.error(
                "Please enter a valid Date of Birth "
                "above first."
            )

        elif not birth_location.strip():

            st.warning(
                "Please enter your birth location."
            )

        else:

            with st.spinner(
                "Calculating your birth chart..."
            ):

                try:

                    # -------------------------------------
                    # FIND LOCATION
                    # -------------------------------------

                    location_data = geocode_location(
                        birth_location.strip()
                    )

                    if location_data is None:

                        st.error(
                            "Birth location could not be found. "
                            "Please enter a valid city/place."
                        )

                        st.stop()

                    latitude, longitude, timezone_name = (
                        location_data
                    )

                    # -------------------------------------
                    # JULIAN DAY
                    # -------------------------------------

                    jd_ut = calculate_julian_day(
                        dob,
                        birth_time,
                        timezone_name
                    )

                    # -------------------------------------
                    # PLANETS
                    # -------------------------------------

                    planets = calculate_planets(
                        jd_ut
                    )

                    # -------------------------------------
                    # ASCENDANT
                    # -------------------------------------

                    ascendant, cusps = (
                        calculate_ascendant(
                            jd_ut,
                            latitude,
                            longitude
                        )
                    )

                    ascendant_sign = get_sign(
                        ascendant
                    )

                    ascendant_degree = (
                        get_degree_in_sign(
                            ascendant
                        )
                    )

                    asc_nakshatra, asc_pada, asc_lord = (
                        get_nakshatra(
                            ascendant
                        )
                    )

                    # -------------------------------------
                    # SUCCESS
                    # -------------------------------------

                    st.success(
                        "Birth chart calculated successfully!"
                    )

                    st.divider()

                    st.header(
                        "🌙 Your Birth Details"
                    )

                    st.write(
                        f"📅 **Date:** "
                        f"{dob.strftime('%d-%m-%Y')}"
                    )

                    st.write(
                        f"🕐 **Time:** "
                        f"{birth_time.strftime('%I:%M %p')}"
                    )

                    st.write(
                        f"📍 **Location:** "
                        f"{birth_location.title()}"
                    )

                    # =====================================
                    # LAGNA
                    # =====================================

                    st.subheader(
                        "🌅 Lagna / Ascendant"
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.metric(
                            "Lagna",
                            ascendant_sign
                        )

                    with col2:

                        st.metric(
                            "Degree",
                            format_degree(
                                ascendant_degree
                            )
                        )

                    with col3:

                        st.metric(
                            "Nakshatra",
                            f"{asc_nakshatra} "
                            f"(Pada {asc_pada})"
                        )

                    # =====================================
                    # SUN & MOON
                    # =====================================

                    st.subheader(
                        "☀️ Sun & 🌙 Moon"
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        st.write(
                            f"☀️ **Sun / Surya**"
                        )

                        st.write(
                            f"Rashi: "
                            f"{planets['Sun']['sign']}"
                        )

                        st.write(
                            f"Degree: "
                            f"{format_degree(planets['Sun']['degree'])}"
                        )

                        st.write(
                            f"Nakshatra: "
                            f"{planets['Sun']['nakshatra']}"
                        )

                    with col2:

                        st.write(
                            f"🌙 **Moon / Chandra**"
                        )

                        st.write(
                            f"Rashi: "
                            f"{planets['Moon']['sign']}"
                        )

                        st.write(
                            f"Degree: "
                            f"{format_degree(planets['Moon']['degree'])}"
                        )

                        st.write(
                            f"Nakshatra: "
                            f"{planets['Moon']['nakshatra']} "
                            f"(Pada {planets['Moon']['pada']})"
                        )

                    # =====================================
                    # PLANETARY POSITIONS
                    # =====================================

                    st.subheader(
                        "🪐 Planetary Positions"
                    )

                    planet_rows = []

                    for planet_name, data in planets.items():

                        house = get_whole_sign_house(
                            data["longitude"],
                            ascendant
                        )

                        planet_rows.append({
                            "Planet": planet_name,
                            "Rashi": data["sign"],
                            "Degree": format_degree(
                                data["degree"]
                            ),
                            "Nakshatra": data["nakshatra"],
                            "Pada": data["pada"],
                            "House": house,
                            "Retrograde": (
                                "Yes"
                                if data["retrograde"]
                                else "No"
                            )
                        })

                    st.dataframe(
                        planet_rows,
                        use_container_width=True,
                        hide_index=True
                    )

                    # =====================================
                    # NAKSHATRA
                    # =====================================

                    st.subheader(
                        "⭐ Birth Nakshatra"
                    )

                    moon_nakshatra = planets[
                        "Moon"
                    ]["nakshatra"]

                    moon_pada = planets[
                        "Moon"
                    ]["pada"]

                    moon_lord = planets[
                        "Moon"
                    ]["nakshatra_lord"]

                    st.write(
                        f"**Nakshatra:** "
                        f"{moon_nakshatra}"
                    )

                    st.write(
                        f"**Pada:** "
                        f"{moon_pada}"
                    )

                    st.write(
                        f"**Nakshatra Lord:** "
                        f"{moon_lord}"
                    )

                    # =====================================
                    # 12 HOUSES
                    # =====================================

                    st.subheader(
                        "🏠 12 Houses / Bhava"
                    )

                    house_rows = []

                    asc_sign_number = int(
                        ascendant // 30
                    )

                    for house_number in range(
                        1,
                        13
                    ):

                        sign_index = (
                            asc_sign_number
                            + house_number
                            - 1
                        ) % 12

                        house_rows.append({
                            "House": (
                                f"{house_number}th House"
                            ),
                            "Rashi": SIGNS[
                                sign_index
                            ]
                        })

                    st.dataframe(
                        house_rows,
                        use_container_width=True,
                        hide_index=True
                    )

                    # =====================================
                    # DASHA
                    # =====================================

                    st.subheader(
                        "🔮 Vimshottari Dasha"
                    )

                    (
                        birth_dasha_lord,
                        dasha_timeline,
                        current_mahadasha,
                        current_antardasha
                    ) = calculate_dasha(
                        dob,
                        planets["Moon"]["longitude"]
                    )

                    st.write(
                        f"**Starting Mahadasha:** "
                        f"{birth_dasha_lord}"
                    )

                    if current_mahadasha:

                        st.success(
                            f"Current Mahadasha: "
                            f"{current_mahadasha['lord']}"
                        )

                    if current_antardasha:

                        st.info(
                            f"Current Antardasha: "
                            f"{current_antardasha['lord']}"
                        )

                    dasha_rows = []

                    for dasha in dasha_timeline:

                        dasha_rows.append({
                            "Mahadasha": dasha["lord"],
                            "Start": dasha[
                                "start"
                            ].strftime(
                                "%d-%m-%Y"
                            ),
                            "End": dasha[
                                "end"
                            ].strftime(
                                "%d-%m-%Y"
                            )
                        })

                    st.dataframe(
                        dasha_rows,
                        use_container_width=True,
                        hide_index=True
                    )

                    # =====================================
                    # YOGAS
                    # =====================================

                    st.subheader(
                        "✨ Yoga Indicators"
                    )

                    yogas = find_yoga_indicators(
                        planets
                    )

                    for yoga in yogas:

                        st.write(
                            f"🔯 {yoga}"
                        )

                    # =====================================
                    # DISCLAIMER
                    # =====================================

                    st.warning(
                        "ℹ️ Birth-chart calculations are based "
                        "on astronomical calculations and "
                        "traditional Vedic astrology rules. "
                        "Astrology interpretations are provided "
                        "for informational purposes."
                    )

                except Exception as error:
                    st.error("Unable to generate the birth chart.")

                    st.error(
                        f"Actual Error: {type(error).__name__}: {error}"
                    )

                    with st.expander("🔍 Error Details"):
                        st.exception(error)
                    