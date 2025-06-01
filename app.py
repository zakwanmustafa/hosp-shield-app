import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Database setup
conn = sqlite3.connect('hospital_data.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS preparedness (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    hospital_name TEXT,
    bed_occupancy INTEGER,
    icu_capacity INTEGER,
    staff_availability INTEGER,
    med_stock INTEGER,
    lab_capacity INTEGER,
    pandemic_severity TEXT,
    active_cases INTEGER,
    spread_rate REAL,
    risk_level TEXT,
    ventilators INTEGER,
    oxygen_supply INTEGER,
    on_duty_staff INTEGER,
    sick_staff INTEGER,
    specialist_avail TEXT,
    ppe_stock INTEGER,
    triage_status TEXT,
    tests_per_day INTEGER,
    tat REAL,
    food_supply_days INTEGER,
    ipc_status TEXT,
    preparedness_score REAL
)
""")
conn.commit()

# UI configuration
st.set_page_config(page_title="HospShield", layout="wide", initial_sidebar_state="expanded")
st.title("HospShield: Hospital Disaster Preparedness Dashboard")

# Sidebar navigation
menu = st.sidebar.radio("Navigation", [
    "Dashboard Overview",
    "External Factors Input",
    "Internal Factors Input",
    "Reports & Recommendations",
    "User Management"
])

# Initialize external factors in session state if not present
if "external_factors" not in st.session_state:
    st.session_state.external_factors = {
        "pandemic_severity": "Unknown",
        "active_cases": 0,
        "spread_rate": 0.0,
        "risk_level": "Unknown"
    }

# Helper function to calculate preparedness score
def calculate_score(data):
    try:
        components = [
            max(0, 100 - data.get('bed_occupancy', 0)),
            max(0, min(100, data.get('icu_capacity', 0))),
            max(0, min(100, data.get('staff_availability', 0))),
            max(0, min(100, data.get('med_stock', 0))),
            max(0, min(100, data.get('lab_capacity', 0))),
        ]
        return round(sum(components) / len(components), 2)
    except Exception:
        return 0.0

# 1. Dashboard Overview
if menu == "Dashboard Overview":
    st.subheader("📊 Dashboard Overview")
    latest = pd.read_sql("SELECT * FROM preparedness ORDER BY date DESC LIMIT 1", conn)

    if not latest.empty:
        score = latest.iloc[0].get('preparedness_score', 0)
        st.metric("Preparedness Score", f"{score}%")
        if score < 50:
            st.error("Low Preparedness")
        elif score < 75:
            st.warning("Moderate Preparedness")
        else:
            st.success("High Preparedness")

        st.write("### Indicators")
        expected_columns = ['bed_occupancy', 'icu_capacity', 'staff_availability', 'med_stock', 'lab_capacity']
        available_columns = [col for col in expected_columns if col in latest.columns]

        if available_columns:
            indicators = latest.loc[:, available_columns].T
            indicators.columns = ['Latest']
            st.bar_chart(indicators)
        else:
            st.warning("No indicator data available to display charts.")
    else:
        st.info("No data available. Please input current status.")

# 2. External Factors Input
elif menu == "External Factors Input":
    st.subheader("🌍 External Factors")
    with st.form("external_form"):
        pandemic_severity = st.selectbox("Pandemic Severity", ["Local", "National", "Global"])
        active_cases = st.number_input("Active Cases", min_value=0, step=1)
        spread_rate = st.number_input("Rate of Spread (R0)", min_value=0.0, format="%.2f")
        risk_level = st.selectbox("Community Risk Level", ["Low", "Moderate", "High"])
        submitted = st.form_submit_button("Save External Factors")
        if submitted:
            st.session_state.external_factors = {
                "pandemic_severity": pandemic_severity,
                "active_cases": active_cases,
                "spread_rate": spread_rate,
                "risk_level": risk_level
            }
            st.success("External factors saved.")

# 3. Internal Factors Input
elif menu == "Internal Factors Input":
    st.subheader("🏥 Internal Factors")
    with st.form("internal_form"):
        hospital_name = st.text_input("Hospital Name", max_chars=100)
        bed_occupancy = st.slider("Bed Occupancy (%)", 0, 100, 75)
        icu_capacity = st.slider("ICU Capacity (%)", 0, 100, 60)
        staff_availability = st.slider("Staff Availability (%)", 0, 100, 85)
        med_stock = st.slider("Medicine Stock (%)", 0, 100, 70)
        lab_capacity = st.slider("Lab Capacity (%)", 0, 100, 80)
        ventilators = st.number_input("Ventilators Available", min_value=0, step=1)
        oxygen_supply = st.number_input("Oxygen Supply Units", min_value=0, step=1)
        on_duty_staff = st.number_input("On-duty Staff Count", min_value=0, step=1)
        sick_staff = st.number_input("Sick/Stressed Staff Count", min_value=0, step=1)
        specialist_avail = st.text_input("Specialist Availability", max_chars=200)
        ppe_stock = st.number_input("PPE Stock Units", min_value=0, step=1)
        triage_status = st.selectbox("Triage Status", ["Functioning", "Delayed", "Overwhelmed"])
        tests_per_day = st.number_input("Tests Per Day", min_value=0, step=1)
        tat = st.number_input("Test Turnaround Time (hours)", min_value=0.0, format="%.2f")
        food_supply_days = st.number_input("Food Supply Reserve (days)", min_value=0, step=1)
        ipc_status = st.selectbox("IPC Status", ["Adequate", "Partial", "Inadequate"])

        submitted = st.form_submit_button("Submit")
        if submitted:
            ext = st.session_state.external_factors
            score = calculate_score({
                'bed_occupancy': bed_occupancy,
                'icu_capacity': icu_capacity,
                'staff_availability': staff_availability,
                'med_stock': med_stock,
                'lab_capacity': lab_capacity
            })
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO preparedness (
                    date, hospital_name, bed_occupancy, icu_capacity, staff_availability, med_stock, lab_capacity,
                    pandemic_severity, active_cases, spread_rate, risk_level, ventilators, oxygen_supply,
                    on_duty_staff, sick_staff, specialist_avail, ppe_stock, triage_status,
                    tests_per_day, tat, food_supply_days, ipc_status, preparedness_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                date, hospital_name, bed_occupancy, icu_capacity, staff_availability, med_stock, lab_capacity,
                ext['pandemic_severity'], ext['active_cases'], ext['spread_rate'], ext['risk_level'],
                ventilators, oxygen_supply, on_duty_staff, sick_staff, specialist_avail, ppe_stock,
                triage_status, tests_per_day, tat, food_supply_days, ipc_status, score
            ))
            conn.commit()
            st.success(f"Data saved successfully! Preparedness Score: {score}%")

# 4. Reports & Recommendations
elif menu == "Reports & Recommendations":
    st.subheader("📋 Reports & Recommendations")
    df = pd.read_sql("SELECT * FROM preparedness ORDER BY date DESC", conn)
    if df.empty:
        st.info("No preparedness data available.")
    else:
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "preparedness_data.csv", "text/csv")

        latest = df.iloc[0]
        st.markdown("### Recommendations based on latest data:")
        recs = []
        if latest['preparedness_score'] < 50:
            recs.append("- Urgent: Increase PPE stocks immediately.")
            recs.append("- Review staff rotation and surge capacity plans.")
            recs.append("- Boost laboratory and surveillance capacity.")
        elif latest['preparedness_score'] < 75:
            recs.append("- Moderate preparedness: Monitor medicine stock closely.")
            recs.append("- Prepare to scale up triage and IPC measures if cases rise.")
        else:
            recs.append("- High preparedness: Maintain current protocols and readiness.")

        for rec in recs:
            st.write(rec)

# 5. User Management (Placeholder)
elif menu == "User Management":
    st.subheader("👥 User Management & Audit Trails")
    st.info("Role-based access control, audit logs, and digital acknowledgment features coming soon.")

# Close DB connection on exit
def close_conn():
    conn.close()

import atexit
atexit.register(close_conn)
