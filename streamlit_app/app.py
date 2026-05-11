import streamlit as st 
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# use this line if running locally
# FASTAPI_URL = os.getenv("FASTAPI_URL")
# uploaded to streamlit community- using st.secrets instead of .env setup
FASTAPI_URL = st.secrets["FASTAPI_URL"]

# note- page_title in this config is the title in thr browser tab
st.set_page_config(page_title="Predictive Maintanence", layout="wide")

# title actually on the webpage
st.title("Predictive Maintanence App")
st.write("Enter sensor readings to predict equipment failure.")

# get the boxes to fill out info ready
# include min value, max value, formats if decimal, and default values (equivalent to row 1 on the Postgres DB)
# note: min and max values were picked from whole number above/below the true min and max values of each column in the DB

# note for machine type- we have to convert the text in the select box to the character L M or H so you 
# can pass in a lambda to mask what the actual value is behind the selection
machine_type = st.selectbox(
    "Machine Quality Type",
    options=["L", "M", "H"],
    format_func=lambda x: {"L": "Low (L)", "M": "Medium (M)", "H": "High (H)"}[x]
)
air_temp = st.number_input("Air Temperature (K): Range 290.0 -> 320.0", min_value=290.0, max_value=320.0, value=298.1, step=0.1, format="%.1f")
process_temp = st.number_input("Process Temperature (K): Range 300.0 -> 320.0", min_value=300.0, max_value=320.0, value=308.6, step=0.1, format="%.1f")
rotation_speed = st.number_input("Rotational Speed (RPM): Range 1100 -> 2900", min_value=1100, max_value=2900, value=1551, step=1)
torque = st.number_input("Torque (NM): Range 0.0 -> 80.0", min_value=0.0, max_value=80.0, value=42.8, step=0.1, format="%.1f")
tool_wear = st.number_input("Tool Wear (MIN): Range 0 -> 253", min_value=0, max_value=253, value=0, step=1)

# add the button to call the /predict function in fastapi
if st.button("Predict", type="primary"):
    # format of JSON that /predict expects
    payload = {
        "type": machine_type,
        "air_temperature": air_temp,
        "process_temperature": process_temp,
        "rotational_speed": int(rotation_speed),
        "torque": torque,
        "tool_wear": int(tool_wear),
    }

    # st spinner shows a loading animation while the request runs
    with st.spinner("Running prediction..."):
        try:
            response = requests.post(f"{FASTAPI_URL}/predict", json=payload, timeout=60)
            # this gets all 400 and 500 errors and returns exceptions so i can
            # add exception handling to this to read errors
            response.raise_for_status()
            # storing in result makes it stay on screen until i press the button for another prediction again
            st.session_state.result = response.json()

        # if i get a timeout we need to halt the request so it doesnt load forever
        except requests.exceptions.Timeout:
            st.error("Request timed out — the API may be cold-starting. Try again.")
            st.stop()
        except requests.exceptions.RequestException as e:
            st.error(f"API error: {e}")
            st.stop()

# check if there is a result in session state (aka the result of the last time predict was pressed)
# note: EVERY TIME YOU INTERACT, THE WHOLE SCRIPT GETS RERUN- so session state will hold values even on a re run
if "result" in st.session_state:
    result = st.session_state.result
    label = result["label"]
    prob = result["probability"]

    # log two metrics in columns with their info
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Result", label)
    with col2:
        st.metric("Failure Probability", f"{prob:.1%}")