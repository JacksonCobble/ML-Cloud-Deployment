import streamlit as st 

# note- page_title in this config is the title in thr browser tab
st.set_page_config(page_title="Predictive Maintanence", layout="wide")

# title actually on the webpage
st.title("Predictive Maintanence App")
st.write("Enter sensor readings to predict equipment failure.")

# get the boxes to fill out info ready
# include min value, max value, formats if decimal, and default values (equivalent to row 1 on the Postgres DB)
# note: min and max values were picked from whole number above/below the true min and max values of each column in the DB
machine_type = st.selectbox("Machine Type Quality", options=["Low (L)", "Medium (M)", "High (H)"])
air_temp = st.number_input("Air Temperature (K): Range 290.0 -> 320.0", min_value=290.0, max_value=320.0, value=298.1, step=0.1, format="%.1f")
process_temp = st.number_input("Process Temperature (K): Range 300.0 -> 320.0", min_value=300.0, max_value=320.0, value=308.6, step=0.1, format="%.1f")
rotation_speed = st.number_input("Rotational Speed (RPM): Range 1100 -> 2900", min_value=1100, max_value=2900, value=1551, step=1)
torque = st.number_input("Torque (NM): Range 0.0 -> 80.0", min_value=0.0, max_value=80.0, value=42.8, step=0.1, format="%.1f")
tool_wear = st.number_input("Tool Wear (MIN): Range 0 -> 253", min_value=0, max_value=253, value=0, step=1)