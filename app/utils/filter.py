import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
from process_messages.process_messages import ProcessMessages

load_dotenv()
FILE_PATH = os.getenv("FILE_PATH")

common_cols = ["sender", "datetime"]


@st.cache_data
def load_data():
    process_messages = ProcessMessages(FILE_PATH)
    text_message = process_messages.get_text_messages()
    calls = process_messages.get_calls_df()
    media = process_messages.get_midia_messages()

    return text_message, calls, media


text_message_df, calls_df, media_df = load_data()


def concat_all_data():
    common_cols = ["sender", "datetime"]
    dfs = [(text_message_df, "text"), (calls_df, "call"), (media_df, "media")]

    valid_dfs = []
    for df, label in dfs:
        if not df.empty and all(col in df.columns for col in common_cols):
            temp_df = df[common_cols].copy()
            temp_df["type"] = label
            valid_dfs.append(temp_df)

    if not valid_dfs:
        return pd.DataFrame(columns=common_cols + ["type"])

    merged_df = pd.concat(valid_dfs, ignore_index=True)
    return merged_df.sort_values(by="datetime").reset_index(drop=True)
