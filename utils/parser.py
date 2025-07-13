import pandas as pd
import re
from io import StringIO

def parse_chat(file):
    # import streamlit as st
    content = file.read().decode("utf-8")
    # Try to match both 24-hour and 12-hour time formats, with or without AM/PM
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2})(?: ?([APMapm]{2}))? - ([^:]+): (.*)'
    matches = re.findall(pattern, content)
    # st.write("[DEBUG] Number of chat message matches:", len(matches))
    data = []
    for date, time, ampm, sender, message in matches:
        dt_str = f"{date} {time}"
        if ampm:
            dt_str += f" {ampm}"
        data.append({
            "datetime": dt_str,
            "sender": sender,
            "message": message
        })
    # st.write("[DEBUG] First 5 parsed messages:", data[:5])
    df = pd.DataFrame(data)
    if not df.empty:
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce', dayfirst=True)
        df['date'] = df['datetime'].dt.date
        df['hour'] = df['datetime'].dt.hour
        df['weekday'] = df['datetime'].dt.day_name()
    return df
