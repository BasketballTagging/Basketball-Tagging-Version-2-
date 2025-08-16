import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Basketball Tagging App", layout="wide")

# --- Initialize Session State ---
if "plays" not in st.session_state:
    st.session_state.plays = []

if "data" not in st.session_state:
    st.session_state.data = []

# --- Sidebar Inputs ---
st.sidebar.header("Game Setup")
opponent = st.sidebar.text_input("Opponent")
game_date = st.sidebar.date_input("Game Date", value=date.today())
quarter = st.sidebar.selectbox("Quarter", ["", "1", "2", "3", "4", "OT"])

# Only allow tagging if all game info is filled
ready_to_tag = opponent and game_date and quarter

st.sidebar.markdown("---")
st.sidebar.subheader("Playbook")

# Add new play
new_play = st.sidebar.text_input("Add New Play")
if st.sidebar.button("ADD NEW PLAY") and new_play:
    if new_play not in st.session_state.plays:
        st.session_state.plays.append(new_play)
    else:
        st.sidebar.warning("Play already exists!")
    st.sidebar.text_input("Add New Play", value="", key="reset_play_input")  # reset input field

# --- Main Area ---
st.title("🏀 Basketball Tagging Application")

if not ready_to_tag:
    st.warning("Please select Opponent, Game Date, and Quarter in the sidebar before tagging plays.")
else:
    st.write(f"**Game:** vs {opponent} | Date: {game_date} | Quarter: {quarter}")

    # Show play buttons
    for play in st.session_state.plays:
        if st.button(play):
            st.session_state.selected_play = play

    # If a play is selected, show tagging options
    if "selected_play" in st.session_state:
        st.subheader(f"Tagging: {st.session_state.selected_play}")
        col1, col2, col3, col4, col5 = st.columns(5)

        if col1.button("Made 2"):
            st.session_state.data.append([st.session_state.selected_play, "Made 2", 2])
        if col2.button("Made 3"):
            st.session_state.data.append([st.session_state.selected_play, "Made 3", 3])
        if col3.button("Missed 2"):
            st.session_state.data.append([st.session_state.selected_play, "Missed 2", 0])
        if col4.button("Missed 3"):
            st.session_state.data.append([st.session_state.selected_play, "Missed 3", 0])
        if col5.button("Foul"):
            st.session_state.data.append([st.session_state.selected_play, "Foul", 0])

    # --- Build Metrics Table ---
    if st.session_state.data:
        df = pd.DataFrame(st.session_state.data, columns=["Play", "Result", "Points"])

        metrics = df.groupby("Play").agg(
            Attempts=("Result", "count"),
            Points=("Points", "sum"),
        ).reset_index()

        metrics["PPP"] = metrics["Points"] / metrics["Attempts"]
        total_attempts = metrics["Attempts"].sum()
        metrics["Frequency"] = metrics["Attempts"] / total_attempts
        # Success rate = FG made / FG attempts (exclude fouls)
        success = df[df["Result"].isin(["Made 2", "Made 3"])].groupby("Play").size()
        attempts_no_fouls = df[df["Result"].isin(["Made 2", "Made 3", "Missed 2", "Missed 3"])].groupby("Play").size()
        metrics["Success Rate"] = metrics["Play"].map(lambda x: success.get(x, 0) / attempts_no_fouls.get(x, 1))

        st.subheader("📊 Per Play Metrics")
        st.dataframe(metrics.style.format({
            "PPP": "{:.2f}",
            "Frequency": "{:.1%}",
            "Success Rate": "{:.1%}"
        }))

        # --- Export to CSV ---
        csv = metrics.to_csv(index=False).encode("utf-8")
        filename = f"{opponent}_{game_date}_Q{quarter}_metrics.csv"
        st.download_button(
            label="📥 Download Metrics as CSV",
            data=csv,
            file_name=filename,
            mime="text/csv",
        )
