import re
import pandas as pd
from dataclasses import dataclass, field
from datetime import datetime


text_message_pattern = re.compile(r'^\s*\[(\d{2}/\d{2}/\d{2}), (\d{2}:\d{2}:\d{2})\] (.*?): (.*)')
call_message_pattern = re.compile(r'^\s*\[(\d{2}/\d{2}/\d{2}), (\d{2}:\d{2}:\d{2})\] (.*?): (.*). \u200e(\d) (.*)')


@dataclass
class ProcessMessages:
    file_path: str
    all_messages: list = field(init=False)

    def __post_init__(self):
        self.get_all_messages()

    def get_text_messages(self):
        all_text_message = []
        for message in self.all_messages:
            match = text_message_pattern.match(message)
            if match and not (
                    self.is_call(message) or self.is_media(message) or '\u200eThis message was deleted.' in message):
                date_str, time_str, sender, content = match.groups()
                dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%y %H:%M:%S")
                all_text_message.append({"datetime": dt, "sender": sender, "message": content})

        return pd.DataFrame(all_text_message)

    def get_calls_df(self):
        all_calls = []
        for message in self.all_messages:
            match = text_message_pattern.match(message)
            if match and self.is_call(message):
                date = datetime.strptime(message.split(']')[0][1:], "%d/%m/%y, %H:%M:%S")
                sender = message.split(']')[1].split(':')[0].strip()
                normalized_message = message.replace('\u200e', '').lower()
                is_missed = 'missed' in normalized_message or 'no answer' in normalized_message
                is_video = 'video' in message
                duration = self.get_call_duration(message, is_missed)

                all_calls.append({'datetime': date, 'sender': sender, 'is_video': is_video, 'is_missed': is_missed,
                                  'duration': duration})

        return pd.DataFrame(all_calls)

    def get_call_duration(self, message, is_missed):
        formatted_message = message.replace('\u200e', '')
        type = formatted_message.split()[-1]
        time = formatted_message.split()[-2]
        if not is_missed:
            if type == 'sec':
                return int(time)
            if type == 'min':
                return int(time) * 60
            if type == 'hr':
                return int(time) * 60 * 60

    def get_midia_messages(self):
        all_midia_message = []
        for message in self.all_messages:
            match = text_message_pattern.match(message)
            if match and self.is_media(message):
                message = message.replace('\u200e', '')
                date = datetime.strptime(message.split(']')[0][1:], "%d/%m/%y, %H:%M:%S")
                sender = message.split(']')[1].split(':')[0].strip()
                type = 'document' if 'document' in message else message.split(':')[-1].replace(' omitted', '')
                all_midia_message.append({'datetime': date, 'sender': sender, 'type': type})
        return pd.DataFrame(all_midia_message)

    def is_media(self, message):
        return '\u200eimage omitted' in message or '\u200esticker omitte' in message or '\u200evideo omitted' in message or '\u200eaudio omitted' in message or '\u200eGIF omitted' in message or 'document omitted' in message or '\u200eContact card omitted' in message

    def is_call(self, message):
        return '\u200eVoice call.' in message or '\u200eVideo call.' in message or '\u200eMissed voice call.' in message or '\u200eMissed video call. \u200eTap to call back' in message

    def get_all_messages(self):
        all_messages = ' '
        with open(self.file_path, "r", encoding="utf-8") as file:
            for line in file:
                all_messages += line.rstrip('\n')

        pattern = r'(?=\[\d{2}/\d{2}/\d{2}, \d{2}:\d{2}:\d{2}\])'
        messages = re.split(pattern, all_messages)
        self.all_messages = [msg for msg in messages if msg.strip()]