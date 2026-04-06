from __future__ import annotations

import pandas as pd
import streamlit as st


def render_admin_dashboard(records: pd.DataFrame) -> None:
    st.markdown("## Admin Dashboard")

    if records.empty:
        st.info("No student records found yet.")
        return

    filter_col_1, filter_col_2 = st.columns(2)
    with filter_col_1:
        usn_filter = st.text_input("Filter by USN", placeholder="Enter USN")
    with filter_col_2:
        mode_options = ["All"] + sorted(records["mode"].dropna().astype(str).str.upper().unique().tolist())
        selected_mode = st.selectbox("Filter by Mode", mode_options)

    filtered = records.copy()
    filtered["mode"] = filtered["mode"].astype(str)
    filtered["usn"] = filtered["usn"].astype(str)

    if usn_filter.strip():
        filtered = filtered[filtered["usn"].str.contains(usn_filter.strip(), case=False, na=False)]
    if selected_mode != "All":
        filtered = filtered[filtered["mode"].str.upper() == selected_mode]

    metric_col_1, metric_col_2 = st.columns(2)
    with metric_col_1:
        average_score = float(filtered["average_score"].fillna(0).mean()) if not filtered.empty else 0.0
        st.metric("Average Score", f"{average_score:.1f}/10")
    with metric_col_2:
        st.metric("Total Attempts", int(len(filtered)))

    st.markdown("### Student Records")
    st.dataframe(
        filtered.sort_values("date", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    leaderboard = (
        records.assign(average_score=records["average_score"].fillna(0))
        .groupby(["usn", "name"], as_index=False)["average_score"]
        .max()
        .sort_values("average_score", ascending=False)
        .head(10)
        .rename(columns={"average_score": "best_average_score"})
    )

    st.markdown("### Leaderboard")
    st.dataframe(leaderboard, use_container_width=True, hide_index=True)
