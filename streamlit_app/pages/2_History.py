import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

# note- page_title in this config is the title in thr browser tab
st.set_page_config(page_title="Prediction History", layout="wide")
st.title("Prediction History")

# cached resources- global resources that are shared across ALL runs
@st.cache_resource
# the first time its called it calls create engine, but every subsequent run
# the return value is remembered and just returned back without having to run
# the code
def get_engine():
    # use this line if running locally
    # url = os.getenv("DATABASE_URL")
    # uploaded to streamlit community- using st.secrets instead of .env setup
    url = st.secrets["DATABASE_URL"]
    return create_engine(url)

# loads all predictions from the prediction table and retur4ns as df
def load_predictions(engine):
    # sql command to get all columns except the id one - should use text() to wrap commands- remember that
    query = text("""
        SELECT
            timestamp, type,
            air_temperature, process_temperature,
            rotational_speed, torque, tool_wear,
            prediction, prediction_label, probability_failure
        FROM predictions
        ORDER BY timestamp DESC
    """)
    # pull data and store in df
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df

# init state on first load
if "history_df" not in st.session_state:
    st.session_state.history_df = None

engine = get_engine()

# using session state to hold the table so it doesnt get deleted on reruns
# auto load on first visit (state is None)
if st.session_state.history_df is None:
    with st.spinner("Loading history..."):
        st.session_state.history_df = load_predictions(engine)

# refresh button — triggers a rerun when clicked
if st.button("Refresh data", type="primary"):
    with st.spinner("Querying database..."):
        st.session_state.history_df = load_predictions(engine)


df = st.session_state.history_df
# make sure to map the L M H numeric values back to caterogircal ones that make sense
df["type"] = df["type"].map({0: "Low", 1: "Medium", 2: "High"})

# make sure theres no tomfoolery ater pulling from the DB
if df is not None and not df.empty:
    st.subheader(f"Showing {len(df)} predictions")
    # we can just load a df as an entire table :D
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "timestamp": st.column_config.DatetimeColumn("Timestamp", format="YYYY-MM-DD HH:mm:ss"),
            "type": st.column_config.TextColumn("Machine Quality Type"),
            "air_temperature": st.column_config.NumberColumn("Air Temp (K)", format="%.1f"),
            "process_temperature": st.column_config.NumberColumn("Process Temp (K)", format="%.1f"),
            "rotational_speed": st.column_config.NumberColumn("RPM"),
            "torque": st.column_config.NumberColumn("Torque (Nm)", format="%.1f"),
            "tool_wear": st.column_config.NumberColumn("Tool Wear (min)"),
            "prediction_label": st.column_config.TextColumn("Result"),
            "probability_failure": st.column_config.ProgressColumn(
                "Failure Probability", format="%.2f", min_value=0, max_value=1
            ),
        },
    )
# case for it being empty (just in case i ever empty the predictions table in the future)
elif df is not None and df.empty:
    st.info("No predictions yet. Run some on the main page first.")