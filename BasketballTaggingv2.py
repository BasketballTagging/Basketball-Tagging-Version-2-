
import streamlit as st
import pandas as pd
from io import StringIO

# --- SESSION STATE INITIALIZATION ---
if "play_log" not in st.session_state:
    st.session_state.play_log = pd.DataFrame(columns=["Quarter", "Play", "Outcome"])

if "play_metrics" not in st.session_state:
    st.session_state.play_metrics = pd.DataFrame(columns=[
        "Play", "Attempts", "Points", "Points per Possession", "Frequency", "Success Rate"
    ])


# --- SIDEBAR INPUTS ---
st.sidebar.header("Game Info")
opponent = st.sidebar.text_input("Opponent")
game_date = st.sidebar.date_input("Game Date")
quarter = st.sidebar.selectbox("Quarter", ["Q1", "Q2", "Q3", "Q4"])

# Define play types
play_types = ["Pick & Roll", "Isolation", "Post Up", "Transition", "Spot Up"]

st.sidebar.subheader("Select a Play")

# --- OUTCOME HANDLER ---
def add_play(play, outcome):
    # Update Play Log
    st.session_state.play_log = pd.concat([
        st.session_state.play_log,
        pd.DataFrame([{"Quarter": quarter, "Play": play, "Outcome": outcome}])
    ], ignore_index=True)

    # Update Metrics Table
    metrics = st.session_state.play_metrics.set_index("Play")

    # Calculate points
    points_map = {
        "Made 2": 2,
        "Made 3": 3,
        "Missed 2": 0,
        "Missed 3": 0,
        "Foul": 0
    }
    points = points_map[outcome]

    # Update or create play row
    if play not in metrics.index:
        metrics.loc[play] = [0, 0, 0, 0, 0]  # placeholder row

    metrics.loc[play, "Attempts"] += 1
    metrics.loc[play, "Points"] += points
    metrics.loc[play, "Points per Possession"] = metrics.loc[play, "Points"] / metrics.loc[play, "Attempts"]
    metrics.loc[play, "Frequency"] = metrics.loc[play, "Attempts"] / st.session_state.play_log.shape[0]
    metrics.loc[play, "Success Rate"] = (
        len(st.session_state.play_log[(st.session_state.play_log["Play"] == play) &
                                      (st.session_state.play_log["Outcome"].str.contains("Made"))])
        / metrics.loc[play, "Attempts"]
    )

    # Save back
    st.session_state.play_metrics = metrics.reset_index()


# --- PLAY BUTTONS ---
for play in play_types:
    if st.sidebar.button(play):
        outcome = st.radio("Select Outcome for " + play, 
                           ["Made 2", "Made 3", "Missed 2", "Missed 3", "Foul"], key=play)
        if st.button(f"Confirm {play} - {outcome}"):
            add_play(play, outcome)
            st.experimental_rerun()


# --- DISPLAY TABLES ---
st.title("🏀 Basketball Tagging App")

if opponent and game_date:
    st.subheader(f"Game vs {opponent} on {game_date}")

st.markdown("### Table 1: Play Log")
st.dataframe(st.session_state.play_log)

# Export Play Log
if not st.session_state.play_log.empty:
    csv_log = st.session_state.play_log.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Play Log (CSV)",
        data=csv_log,
        file_name=f"play_log_{opponent}_{game_date}.csv",
        mime="text/csv"
    )

st.markdown("### Table 2: Per Play Metrics")
st.dataframe(st.session_state.play_metrics.style.format({
    "Points per Possession": "{:.2f}",
    "Frequency": "{:.2%}",
    "Success Rate": "{:.2%}"
}))

# Export Metrics
if not st.session_state.play_metrics.empty:
    csv_metrics = st.session_state.play_metrics.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Per Play Metrics (CSV)",
        data=csv_metrics,
        file_name=f"play_metrics_{opponent}_{game_date}.csv",
        mime="text/csv"
    )
