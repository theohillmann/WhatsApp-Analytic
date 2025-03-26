import os
from dataclasses import dataclass, field
from dotenv import load_dotenv
import streamlit as st
from process_messages.process_messages import ProcessMessages
from utils.filter import concat_all_data
import pandas as pd
import plotly.graph_objects as go

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

    def show(self):
        self.total_messages()

    def total_messages(self):
        senders = self.all_df["sender"].unique()
        st.write(senders)


Summary().show()
