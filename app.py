import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Laytime Genie", layout="wide")

st.title("⚓ Laytime Genie ⚓")
st.write("===========शं नो वरुणः===========")
st.write("Upload a Statement of Facts (SOF) file and calculate Laytime, Demurrage, or Despatch.")

# File uploader
uploaded_file = st.file_uploader("📂 Upload SOF (CSV format)", type=["csv"])

if uploaded_file:
    # Read the CSV
    df = pd.read_csv(uploaded_file)

    st.subheader("📑 Uploaded SOF Data")
    st.dataframe(df)

    # Ensure proper datetime format
    df["Start"] = pd.to_datetime(df["Start"])
    df["End"] = pd.to_datetime(df["End"])

    # Calculate duration (in hours)
    df["Duration (hrs)"] = (df["End"] - df["Start"]).dt.total_seconds() / 3600

    # Separate Used vs Excluded
    used_time = df[df["Type"].str.lower() == "used"]["Duration (hrs)"].sum()
    excluded_time = df[df["Type"].str.lower() == "excluded"]["Duration (hrs)"].sum()

    st.subheader("📊 Calculations")
    st.write(f"⏳ **Total Used Laytime:** {used_time:.2f} hours")
    st.write(f"🚫 **Excluded Time:** {excluded_time:.2f} hours")

    # Allowed Laytime input
    allowed = st.number_input("Enter Allowed Laytime (in hours)", min_value=1, value=72)

    # Compare
    if used_time > allowed:
        extra = used_time - allowed
        st.error(f"⚠️ Demurrage: Laytime exceeded by {extra:.2f} hours.")
    else:
        saved = allowed - used_time
        st.success(f"✅ Despatch: Laytime saved {saved:.2f} hours.")

    # 📈 Timeline visualization
    st.subheader("📈 Event Timeline")
    fig = px.timeline(
        df,
        x_start="Start",
        x_end="End",
        y="Event",
        color="Type",
        title="SOF Event Timeline",
        labels={"Event": "Operation", "Type": "Category"},
    )

    fig.update_yaxes(autorange="reversed")  # Gantt chart style
    st.plotly_chart(fig, use_container_width=True)
