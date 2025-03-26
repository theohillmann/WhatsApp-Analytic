import pandas as pd
import streamlit as st
from dataclasses import dataclass


@dataclass
class CallsWidget:
    calls_df: pd.DataFrame

    def __post_init__(self):
        self.senders = self.calls_df["sender"].unique()

    def show(self):
        calls_stats = self.calculate_calls()
        self._display_stats(calls_stats)

    def _display_stats(self, calls_stats):
        senders = ["Total"] + list(self.senders)
        stats_config = [
            (
                "All Calls",
                lambda stats: stats["video"]["total"] + stats["voice"]["total"],
            ),
            ("Voice Calls", lambda stats: stats["voice"]["total"]),
            ("Video Calls", lambda stats: stats["video"]["total"]),
        ]

        for title, stat_calculator in stats_config:
            st.subheader(title)
            cols = st.columns(len(senders))
            for col, sender in zip(cols, senders):
                with col:
                    value = self._calculate_total(calls_stats, sender, stat_calculator)
                    st.metric(label="Total", value=value)

    def _calculate_total(self, calls_stats, sender, stat_calculator):
        if sender == "Total":
            return sum(stat_calculator(stats) for stats in calls_stats.values())
        return stat_calculator(calls_stats[sender])

    def calculate_calls(self):
        return {sender: self._get_sender_stats(sender) for sender in self.senders}

    def _get_sender_stats(self, sender):
        sender_calls = self.calls_df[self.calls_df["sender"] == sender]

        return {
            "video": self._get_call_stats(sender_calls, is_video=True),
            "voice": self._get_call_stats(sender_calls, is_video=False),
        }

    def _get_call_stats(self, calls, is_video):
        filtered_calls = calls[calls["is_video"] == is_video]
        missed_calls = filtered_calls[filtered_calls["is_missed"] == True]

        return {
            "total": len(filtered_calls),
            "missed": len(missed_calls),
            "time": filtered_calls["duration"].sum(),
        }
