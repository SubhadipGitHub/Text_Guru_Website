import os
import re
from flask import Flask, render_template, request
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import warnings

from collections import Counter
from datetime import datetime
import random
import nltk

app = Flask(__name__)

nltk.download('vader_lexicon')
sentiments = SentimentIntensityAnalyzer()

# Suppress the UserWarning related to date parsing
warnings.filterwarnings("ignore", category=UserWarning)

def extract_chat_info(file_path):
    participants = set()
    chat_dates = []
    total_chats = 0

    with open(file_path, encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            # Extract participants
            match = re.match(r'^[0-9/]+, [0-9:]+ - (.*?):', line)
            if match:
                participants.add(match.group(1))

            # Extract chat dates
            date_match = re.match(r'^([0-9/]+), [0-9:]+ -', line)
            if date_match:
                chat_date = datetime.strptime(date_match.group(1), "%d/%m/%y").date()
                chat_dates.append(chat_date)

            total_chats += 1

    # Count occurrences of each date
    date_counter = Counter(chat_dates)
    most_chats_day = date_counter.most_common(1)[0][0].strftime("%A")

    start_date = min(chat_dates).strftime("%B %d, %Y")

    return {
        'participants': ' & '.join(participants),
        'start_date': start_date,
        'total_chats': total_chats,
        'most_chats_day': most_chats_day
    }

def extract_random_chat(file_path):
    data = []
    with open(file_path, encoding="utf-8") as fp:
        fp.readline()
        message_buffer = []
        date, time, author = None, None, None
        while True:
            line = fp.readline()
            if not line:
                break
            line = line.strip()
            if date_time(line):
                if len(message_buffer) > 0:
                    # Concatenate (Date) Author : Message
                    chat = f"({date}) {author} : {' '.join(message_buffer)}"
                    data.append(chat)
                message_buffer.clear()
                date, time, author, message = get_datapoint(line)
                message_buffer.append(message)
            else:
                message_buffer.append(line)

    # Randomly select 10 consecutive chats
    start_index = random.randint(0, len(data) - 20)
    selected_chats = data[start_index:start_index + 20]

    return selected_chats

def analyze_sentiment(file_path):
    data = []
    with open(file_path, encoding="utf-8") as fp:
        fp.readline()
        message_buffer = []
        date, time, author = None, None, None
        while True:
            line = fp.readline()
            if not line:
                break
            line = line.strip()
            if date_time(line):
                if len(message_buffer) > 0:
                    data.append([date, time, author, ' '.join(message_buffer)])
                message_buffer.clear()
                date, time, author, message = get_datapoint(line)
                message_buffer.append(message)
            else:
                message_buffer.append(line)

    df = pd.DataFrame(data, columns=["Date", 'Time', 'Author', 'Message'])
    df['Date'] = pd.to_datetime(df['Date'])

    # Set values using .loc to avoid the warning
    df.loc[:, "Compound"] = [sentiments.polarity_scores(i)["compound"] for i in df["Message"]]

    overall_sentiment = sum(df["Compound"])

    sentiment_result = None
    if overall_sentiment >= 0.05:
        sentiment_result = "Positive 😊"
    elif overall_sentiment <= -0.05:
        sentiment_result = "Negative 😠"
    else:
        sentiment_result = "Neutral 🙂"

    return round(overall_sentiment,0), sentiment_result

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')

        file = request.files['file']

        if file.filename == '':
            return render_template('index.html', error='No selected file')

        if file:
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)

            overall_sentiment, sentiment_result = analyze_sentiment(file_path)
            chat_info = extract_chat_info(file_path)
            #print(chat_info)
            # Replace this with your logic to get random chat moments
            random_chat_moments = [
                "Hey, how are you?",
                "Check out this funny meme!",
                "Remember that time we went to the beach?",
                # Add more chat moments
            ]
            ran_chat = extract_random_chat(file_path)
            print(ran_chat)

            return render_template('result.html', overall_sentiment=overall_sentiment, sentiment_result=sentiment_result,overall_sentiment_percentage=overall_sentiment,chat_info=chat_info,random_chat_moments=ran_chat)

    return render_template('index.html', error=None)

# About route
@app.route('/about')
def about():
    return render_template('about.html')

def date_time(s):
    pattern = '^([0-9]+)(\/)([0-9]+)(\/)([0-9]+), ([0-9]+):([0-9]+)[ ]?(AM|PM|am|pm)? -'
    result = re.match(pattern, s)
    if result:
        return True
    return False

def find_author(s):
    s = s.split(":")
    if len(s) == 2:
        return True
    else:
        return False

def get_datapoint(line):
    split_line = line.split(' - ')
    date_time = split_line[0]
    date, time = date_time.split(", ")
    message = " ".join(split_line[1:])
    if find_author(message):
        split_message = message.split(": ")
        author = split_message[0]
        message = " ".join(split_message[1:])
    else:
        author = None
    return date, time, author, message

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True) 
    HOST = '0.0.0.0'
    PORT = 80
    #PORT = 443
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(host=HOST, port=PORT, debug=True)
