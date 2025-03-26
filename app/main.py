import os
from dataclasses import dataclass, field
from dotenv import load_dotenv
import streamlit as st
from process_messages.process_messages import ProcessMessages
from utils.filter import concat_all_data
import pandas as pd
import plotly.graph_objects as go
from collections import defaultdict
from components.general_statistics.general_statistics import Summary
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




Summary().show()
