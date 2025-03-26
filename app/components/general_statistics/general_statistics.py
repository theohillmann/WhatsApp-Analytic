import os
from dataclasses import dataclass, field
from dotenv import load_dotenv
import streamlit as st
from process_messages.process_messages import ProcessMessages
from utils.filter import concat_all_data
import pandas as pd
import plotly.graph_objects as go
from collections import defaultdict
from components.general_statistics.calls_widget.calls_widget import CallsWidget
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


@dataclass
class Summary:
    all_data: pd.DataFrame = field(init=False)

    def __post_init__(self):
        self.all_df = concat_all_data()
        self.senders = self.all_df["sender"].unique()

    def show(self):
        CallsWidget(calls_df).show()



    def total_messages(self):
        cols = st.columns(len(self.senders))

        for col, sender in zip(cols, self.senders):
            with col:
                st.title(sender)
                st.metric(label='text', value=len(self.all_df[(self.all_df["sender"] == sender) & (self.all_df["type"] == "text")]))
                st.metric(label='calls', value=len(self.all_df[(self.all_df["sender"] == sender) & (self.all_df["type"] == "call")]))
                st.metric(label='media', value=len(self.all_df[(self.all_df["sender"] == sender) & (self.all_df["type"] == "media")]))
