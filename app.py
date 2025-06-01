
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Connect to SQLite DB
conn = sqlite3.connect('hospital_data.db', check_same_thread=False)
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS preparedness (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    hospital_name TEXT,
    disaster_management INTEGER,
    bed_occupancy INTEGER,
    staff_availability INTEGER,
    med_stock INTEGER,
    lab_capacity INTEGER,
    preparedness_score REAL
)
""")
conn.commit()

# Title and Sidebar
st.title("HospShield 📊")
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ["Dashboard", "Input Data", "Reports"])

# Dashboard
if menu == "Dashboard":
    st.subheader("📍 Hospital Preparedness Overview")

    cursor.execute("SELECT * FROM preparedness ORDER BY date DESC LIMIT 1")
    latest_data = cursor.fetchone()
    
    if latest_data:
        _, date, name, bed, staff, meds, lab, score = latest_data
        st.write(f"### 🏥 {name} (Last Updated: {date})")
        st.metric("Preparedness Score", f"{score}%")
        st.progress(score / 100)

        st.write("**Indicators**")
        st.write(f"- Bed Occupancy: {bed}%")
        st.write(f"- Staff Availability: {staff}%")
        st.write(f"- Medicine Stock: {meds}%")
        st.write(f"- Lab Capacity: {lab}%")
    else:
        st.info("No data submitted yet. Go to 'Input Data' to begin.")

# Input Data
elif menu == "Input Data":
    st.subheader("📥 Enter Hospital Data")

    with st.form("input_form"):
        name = st.text_input("Hospital Name")
        bed = st.slider("Bed Occupancy (%)", 0, 100, 75)
        staff = st.slider("Staff Availability (%)", 0, 100, 85)
        meds = st.slider("Medicine Stock (%)", 0, 100, 70)
        lab = st.slider("Lab Diagnostic Capacity (%)", 0, 100, 80)
        submitted = st.form_submit_button("Submit")

        if submitted:
            score = round((100 - bed + staff + meds + lab) / 4, 2)
            date = datetime.now().strftime("%Y-%m-%d %H:%M")
            cursor.execute("""
                INSERT INTO preparedness (date, hospital_name, bed_occupancy, staff_availability, med_stock, lab_capacity, preparedness_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (date, name, bed, staff, meds, lab, score))
            conn.commit()
            st.success(f"Data submitted! Preparedness Score: {score}%")

# Reports
elif menu == "Reports":
    st.subheader("📄 Historical Reports")
    df = pd.read_sql("SELECT * FROM preparedness ORDER BY date DESC", conn)
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", data=csv, file_name="hospital_preparedness.csv", mime='text/csv')
