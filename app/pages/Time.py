from dataclasses import dataclass
import os
from dotenv import load_dotenv
import streamlit as st
from click import option
from process_messages.process_messages import ProcessMessages
import pandas as pd
import plotly.express as px
from utils.filter import concat_all_data

if "time" not in st.session_state:
    st.session_state.time = "month"

if "person" not in st.session_state:
    st.session_state.person = "total"

load_dotenv()
FILE_PATH = os.getenv("FILE_PATH")


@st.cache_data
def load_data():
    process_messages = ProcessMessages(FILE_PATH)
    text_message = process_messages.get_text_messages()
    calls = process_messages.get_calls_df()
    media = process_messages.get_midia_messages()

    return text_message, calls, media


text_message_df, calls_df, media_df = load_data()
all_messages = concat_all_data()


@dataclass
class TimePlot:

    def plot(self):
        self.df = all_messages
        self.filter()
        self.df = self.filter_by_person(all_messages)

        self.df["month_year"] = self.df["datetime"].dt.to_period("M")
        self.df["month"] = self.df["datetime"].dt.month
        self.df["day"] = self.df["datetime"].dt.day
        self.df["hour"] = self.df["datetime"].dt.hour
        self.df["hour_minute"] = self.df["datetime"].dt.strftime("%H:%M")

        if st.session_state.person == "Compare":
            if st.session_state.time == "month":
                df_group = (
                    self.df.groupby(["month_year", "sender"])
                    .size()
                    .reset_index(name="count")
                )
                df_group["month_year"] = df_group["month_year"].astype(str)
                fig = px.line(
                    df_group,
                    x="month_year",
                    y="count",
                    color="sender",
                    markers=True,
                    title="Comparação Mensagens por Mês e Ano",
                )
            elif st.session_state.time == "day":
                df_group = (
                    self.df.groupby(["day", "sender"]).size().reset_index(name="count")
                )
                fig = px.line(
                    df_group,
                    x="day",
                    y="count",
                    color="sender",
                    markers=True,
                    title="Comparação Mensagens por Dia",
                )
            elif st.session_state.time == "hour":
                df_group = (
                    self.df.groupby(["hour", "sender"]).size().reset_index(name="count")
                )
                fig = px.line(
                    df_group,
                    x="hour",
                    y="count",
                    color="sender",
                    markers=True,
                    title="Comparação Mensagens por Hora",
                )
            elif st.session_state.time == "minute":
                df_group = (
                    self.df.groupby(["hour_minute", "sender"])
                    .size()
                    .reset_index(name="count")
                )
                fig = px.line(
                    df_group,
                    x="hour_minute",
                    y="count",
                    color="sender",
                    markers=True,
                    title="Comparação Mensagens por Hora e Minuto",
                )
            st.plotly_chart(fig, use_container_width=True)
            return

        if st.session_state.time == "month":
            message_counts = self.df["month_year"].value_counts().sort_index()
        elif st.session_state.time == "day":
            message_counts = self.df["day"].value_counts().sort_index()
        elif st.session_state.time == "hour":
            message_counts = self.df["hour"].value_counts().sort_index()
        elif st.session_state.time == "minute":
            message_counts = self.df["hour_minute"].value_counts().sort_index()

        self.graph_total(message_counts)

    def graph_total(self, message_counts):
        df_plot = message_counts.reset_index()
        df_plot.columns = ["time", "count"]
        df_plot["time"] = df_plot["time"].astype(str)

        fig = px.bar(
            df_plot,
            x="time",
            y="count",
            labels={"time": "Tempo", "count": "Mensagens"},
            title="Mensagens por Tempo",
        )
        st.plotly_chart(fig, use_container_width=True)

    def filter_by_person(self, df):
        if st.session_state.person in ["Total", "Compare"]:
            return df
        return df[df["sender"] == st.session_state.person]

    def filter(self):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.time = st.radio(
                "Time", ["month", "day", "hour", "minute"], horizontal=True
            )
        with col2:
            options = list(self.df["sender"].unique())
            options.extend(["Total", "Compare"])
            st.session_state.person = st.selectbox("Person", options)


if __name__ == "__main__":
    TimePlot().plot()
