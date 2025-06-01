import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Connect to SQLite database
conn = sqlite3.connect("hospital_data.db", check_same_thread=False)
cursor = conn.cursor()

# Create table with consistent column names
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

st.set_page_config(page_title="HospShield", layout="wide")
st.title("HospShield: Hospital Preparedness Dashboard")

menu = st.sidebar.selectbox("Navigation", [
    "Dashboard Overview",
    "Input Data",
    "View Data"
])

def calculate_score(data):
    try:
        score_components = [
            max(0, 100 - data['bed_occupancy']),
            data['icu_capacity'],
            data['staff_availability'],
            data['med_stock'],
            data['lab_capacity']
        ]
        return round(sum(score_components) / len(score_components), 2)
    except Exception as e:
        return 0.0

if menu == "Dashboard Overview":
    st.subheader("📊 Preparedness Overview")
    df = pd.read_sql("SELECT * FROM preparedness ORDER BY date DESC", conn)
    if not df.empty:
        latest = df.iloc[0]
        st.metric("Preparedness Score", f"{latest['preparedness_score']}%")
        st.write("### Latest Indicators")
        indicators = latest[['bed_occupancy', 'icu_capacity', 'staff_availability', 'med_stock', 'lab_capacity']]
        st.bar_chart(indicators.to_frame(name='Value'))
    else:
        st.info("No data available yet.")

elif menu == "Input Data":
    st.subheader("📝 Enter Hospital Data")
    with st.form("input_form"):
        hospital_name = st.text_input("Hospital Name")
        bed_occupancy = st.slider("Bed Occupancy (%)", 0, 100, 70)
        icu_capacity = st.slider("ICU Capacity (%)", 0, 100, 50)
        staff_availability = st.slider("Staff Availability (%)", 0, 100, 80)
        med_stock = st.slider("Medicine Stock (%)", 0, 100, 75)
        lab_capacity = st.slider("Lab Capacity (%)", 0, 100, 85)

        pandemic_severity = st.selectbox("Pandemic Severity", ["Low", "Moderate", "High"])
        active_cases = st.number_input("Active Cases", min_value=0)
        spread_rate = st.number_input("Spread Rate (R0)", min_value=0.0, format="%.2f")
        risk_level = st.selectbox("Community Risk Level", ["Low", "Medium", "High"])

        ventilators = st.number_input("Ventilators Available", min_value=0)
        oxygen_supply = st.number_input("Oxygen Supply Units", min_value=0)
        on_duty_staff = st.number_input("On-duty Staff", min_value=0)
        sick_staff = st.number_input("Sick or Stressed Staff", min_value=0)
        specialist_avail = st.text_input("Specialist Availability")
        ppe_stock = st.number_input("PPE Stock", min_value=0)
        triage_status = st.selectbox("Triage Status", ["Normal", "Delayed", "Overwhelmed"])
        tests_per_day = st.number_input("Tests per Day", min_value=0)
        tat = st.number_input("Test Turnaround Time (hrs)", min_value=0.0, format="%.2f")
        food_supply_days = st.number_input("Food Supply (days)", min_value=0)
        ipc_status = st.selectbox("IPC Status", ["Adequate", "Partial", "Inadequate"])

        submit = st.form_submit_button("Submit Data")

        if submit:
            data = {
                'bed_occupancy': bed_occupancy,
                'icu_capacity': icu_capacity,
                'staff_availability': staff_availability,
                'med_stock': med_stock,
                'lab_capacity': lab_capacity
            }
            score = calculate_score(data)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO preparedness (
                    date, hospital_name, bed_occupancy, icu_capacity, staff_availability,
                    med_stock, lab_capacity, pandemic_severity, active_cases, spread_rate,
                    risk_level, ventilators, oxygen_supply, on_duty_staff, sick_staff,
                    specialist_avail, ppe_stock, triage_status, tests_per_day, tat,
                    food_supply_days, ipc_status, preparedness_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                now, hospital_name, bed_occupancy, icu_capacity, staff_availability,
                med_stock, lab_capacity, pandemic_severity, active_cases, spread_rate,
                risk_level, ventilators, oxygen_supply, on_duty_staff, sick_staff,
                specialist_avail, ppe_stock, triage_status, tests_per_day, tat,
                food_supply_days, ipc_status, score
            ))
            conn.commit()
            st.success(f"Data submitted. Score: {score}%")

elif menu == "View Data":
    st.subheader("📋 Data Records")
    df = pd.read_sql("SELECT * FROM preparedness ORDER BY date DESC", conn)
    if df.empty:
        st.info("No data found.")
    else:
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "preparedness_data.csv", "text/csv")

