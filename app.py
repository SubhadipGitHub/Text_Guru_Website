
import streamlit as st
from utils.parser import parse_chat
from utils.analyzer import generate_statistics, plot_charts
import zipfile
import tempfile
import os

# Ensure NLTK stopwords are available only once at startup
import nltk
try:
    from nltk.corpus import stopwords
    nltk.data.find('corpora/stopwords')
except (ImportError, LookupError):
    nltk.download('stopwords')
    from nltk.corpus import stopwords




st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide", page_icon="💬")

# Sidebar with logo, help, and info
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/whatsapp--v1.png", width=80)
    st.markdown("""
    <h2 style='color:#128c7e;margin-bottom:0;'>WhatsApp Analyzer</h2>
    <div style='font-size:1.1em;'>
    <b>Instructions:</b><br>
    <ul style='margin-top:0;'>
    <li>Export your WhatsApp chat as a <code>.txt/.zip</code> file (or zip).</li>
    <li>Upload it below.</li>
    <li>See instant stats, graphics, and relationship insights!</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    st.info("No data is stored. All analysis is local and private.")
    st.markdown("---")
    st.markdown("<div style='color:#128c7e;font-size:1.1em;'>Made with ❤️ using Streamlit</div>", unsafe_allow_html=True)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(120deg, #f8ffae 0%, #43cea2 100%);
    min-height: 100vh;
}
.st-emotion-cache-1v0mbdj, .st-emotion-cache-1v0mbdj:before {
    background: none !important;
}
.st-emotion-cache-1avcm0n {
    border-radius: 18px;
    box-shadow: 0 6px 32px 0 rgba(67,206,162,0.10);
    background: #fffbe7cc;
}
.st-emotion-cache-1v0mbdj > header {
    background: linear-gradient(90deg, #25d366 0%, #43cea2 100%) !important;
    box-shadow: 0 2px 12px 0 rgba(67,206,162,0.10);
}
.st-emotion-cache-1v0mbdj h1, .st-emotion-cache-1v0mbdj h2 {
    color: #128c7e !important;
    letter-spacing: 1px;
}
.st-emotion-cache-1v0mbdj .stMarkdown {
    font-size: 1.13rem;
}
.st-emotion-cache-1v0mbdj .stDataFrame {
    border-radius: 14px;
    overflow: hidden;
    background: #f8ffae33;
}
.st-emotion-cache-1v0mbdj .stAlert {
    background: linear-gradient(90deg, #f8ffae 0%, #43cea2 100%) !important;
    color: #075e54 !important;
    border-radius: 10px;
}
.st-emotion-cache-1v0mbdj .stInfo {
    background: #e0f7fa !important;
    color: #128c7e !important;
}
.st-emotion-cache-1v0mbdj .stButton>button {
    background: linear-gradient(90deg, #25d366 0%, #43cea2 100%) !important;
    color: #fff !important;
    border-radius: 8px;
    font-weight: 600;
    box-shadow: 0 2px 8px 0 rgba(67,206,162,0.10);
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div style='margin-top: -30px; margin-bottom: 18px;'>
    <h1 style='color:#128c7e; font-size:2.3em; margin-bottom:0.2em;'>WhatsApp Chat Analyzer</h1>
    <div style='font-size:1.18em; color:#075e54;'>Upload your exported WhatsApp chat text file to begin.<br>
    <span style='color:#128c7e;'>All analysis is private and runs in your browser session.</span></div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload .txt or .zip file", type=["txt", "zip"])

from io import BytesIO
def get_txt_file_from_zip(zip_file):
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_file) as z:
            z.extractall(tmpdir)
            for root, _, files in os.walk(tmpdir):
                for file in files:
                    if file.lower().endswith('.txt'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'rb') as f:
                            content = f.read()
                        return BytesIO(content)
    return None

if uploaded_file:
    file_to_read = None
    if uploaded_file.name.lower().endswith('.zip'):
        # st.write("[DEBUG] Uploaded file is a zip archive.")
        file_to_read = get_txt_file_from_zip(uploaded_file)
        if not file_to_read:
            st.error("No .txt file found in the uploaded zip archive.")
    else:
        # st.write("[DEBUG] Uploaded file is a txt file.")
        file_to_read = uploaded_file

    if file_to_read:
        try:
            # file_to_read.seek(0)
            # st.write("[DEBUG] File content sample:", file_to_read.read(500))
            # file_to_read.seek(0)
            chat_df = parse_chat(file_to_read)
            # st.write("[DEBUG] DataFrame columns:", chat_df.columns.tolist() if chat_df is not None else None)
            # st.write("[DEBUG] DataFrame head:", chat_df.head() if chat_df is not None else None)
            if chat_df is None or chat_df.empty or 'datetime' not in chat_df.columns:
                st.error("The uploaded file does not appear to be a valid WhatsApp chat export or is not in the expected format.")
            else:
                st.subheader("📊 Chat Statistics")
                st.markdown(
                    "<span style='color:#25d366;font-size:1.1em;'>Quick stats about your chat group or conversation.</span>", unsafe_allow_html=True)
                stats = generate_statistics(chat_df)
                for key, value in stats.items():
                    st.markdown(f"**{key}**: {value}")

                st.subheader("📈 Visualizations")
                st.markdown(
                    "<span style='color:#128c7e;font-size:1.1em;'>Explore your chat activity with interactive charts.</span>", unsafe_allow_html=True)
                plot_charts(chat_df)

                # --- Enhanced Chat Statistics ---
                st.subheader("🔍 Chatter Details & Timeline")
                st.markdown(
                    "<span style='color:#075e54;font-size:1.1em;'>See who chats the most, when the conversation started, and more.</span>", unsafe_allow_html=True)
                try:
                    # Chatter details
                    st.markdown("#### 👥 Chatter Details")
                    st.dataframe(chat_df['sender'].value_counts().rename('Message Count').reset_index().rename(columns={'index': 'Sender'}))

                    # First and last message
                    first_row = chat_df.sort_values('datetime').iloc[0]
                    last_row = chat_df.sort_values('datetime').iloc[-1]
                    st.markdown(f"- 🟢 **First message:** <span style='color:#128c7e'>{first_row['sender']}</span> on <b>{first_row['datetime'].strftime('%Y-%m-%d %H:%M')}</b><br> <span style='color:#555;'>{first_row['message']}</span>", unsafe_allow_html=True)
                    st.markdown(f"- 🔴 **Last message:** <span style='color:#128c7e'>{last_row['sender']}</span> on <b>{last_row['datetime'].strftime('%Y-%m-%d %H:%M')}</b><br> <span style='color:#555;'>{last_row['message']}</span>", unsafe_allow_html=True)

                    # Enhanced Chatter characteristics
                    st.markdown("#### ✨ Chatter Characteristics")
                    st.info("Below are the most used words, phrases, and who talks about what!")
                    import collections
                    import re
                    try:
                        import nltk
                        from nltk.corpus import stopwords
                        nltk.data.find('corpora/stopwords')
                    except (ImportError, LookupError):
                        import streamlit as st
                        st.info("Downloading NLTK stopwords...")
                        import nltk
                        nltk.download('stopwords')
                        from nltk.corpus import stopwords
                    stop_words = set(stopwords.words('english'))
                    all_msgs = chat_df['message'].str.lower().tolist()
                    all_words = re.findall(r'\b\w+\b', ' '.join(all_msgs))
                    filtered_words = [w for w in all_words if w not in stop_words and len(w) > 2]
                    common_words = collections.Counter(filtered_words).most_common(10)
                    st.markdown("- **Most common words (excl. stopwords):** " + ', '.join([f"<span style='color:#25d366'>{w}</span> ({c})" for w, c in common_words]), unsafe_allow_html=True)

                    # Phrase analysis (bigrams and trigrams)
                    bigrams = zip(filtered_words, filtered_words[1:])
                    trigrams = zip(filtered_words, filtered_words[1:], filtered_words[2:])
                    common_bigrams = collections.Counter(bigrams).most_common(5)
                    common_trigrams = collections.Counter(trigrams).most_common(3)
                    st.markdown("- **Common bigrams:** " + ', '.join([f"<span style='color:#128c7e'>{' '.join(bg)}</span> ({c})" for bg, c in common_bigrams]), unsafe_allow_html=True)
                    st.markdown("- **Common trigrams:** " + ', '.join([f"<span style='color:#128c7e'>{' '.join(tg)}</span> ({c})" for tg, c in common_trigrams]), unsafe_allow_html=True)

                    # Per-sender word clouds (text only)
                    st.markdown("- **Top words per sender:**")
                    for sender in chat_df['sender'].unique():
                        sender_msgs = chat_df[chat_df['sender'] == sender]['message'].str.lower().tolist()
                        sender_words = re.findall(r'\b\w+\b', ' '.join(sender_msgs))
                        sender_filtered = [w for w in sender_words if w not in stop_words and len(w) > 2]
                        top_sender_words = collections.Counter(sender_filtered).most_common(5)
                        st.markdown(f"    - <b>{sender}</b>: " + ', '.join([f"<span style='color:#25d366'>{w}</span> ({c})" for w, c in top_sender_words]), unsafe_allow_html=True)

                    # --- Human-readable characteristics summary ---
                    try:
                        st.markdown("#### 📝 Human Summary of Chat Characteristics")
                        # Message balance
                        senders = chat_df['sender'].value_counts()
                        if len(senders) == 2:
                            user1, user2 = senders.index[0], senders.index[1]
                            ratio = senders.iloc[0] / max(senders.iloc[1], 1)
                            if 0.7 < ratio < 1.3:
                                st.markdown(f"- <span style='color:#25d366'>**Message balance:**</span> {user1} and {user2} both participate equally.", unsafe_allow_html=True)
                            else:
                                st.markdown(f"- <span style='color:#25d366'>**Message balance:**</span> {user1} is more talkative than {user2}.", unsafe_allow_html=True)
                        elif len(senders) > 2:
                            st.markdown(f"- <span style='color:#25d366'>**Group chat:**</span> {len(senders)} participants, top: {', '.join(senders.index[:3])}", unsafe_allow_html=True)
                        # Emoji use
                        emoji_count = chat_df['message'].str.count(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\u2600-\u26FF\u2700-\u27BF]').sum()
                        if emoji_count > 0:
                            st.markdown(f"- <span style='color:#25d366'>**Emoji use:**</span> {int(emoji_count)} emojis used. Expressive and lively communication.", unsafe_allow_html=True)
                        else:
                            st.markdown("- <span style='color:#25d366'>**Emoji use:**</span> Very few emojis. Communication is more formal or reserved.", unsafe_allow_html=True)
                        # Activity
                        active_days = chat_df['date'].nunique()
                        st.markdown(f"- <span style='color:#25d366'>**Active days:**</span> {active_days}. Shows consistency in communication.", unsafe_allow_html=True)
                        # Frequent topics: use most common bigrams/trigrams
                        topic_phrases = []
                        if common_bigrams:
                            topic_phrases += [' '.join(bg) for bg, _ in common_bigrams[:3]]
                        if common_trigrams:
                            topic_phrases += [' '.join(tg) for tg, _ in common_trigrams[:2]]
                        if topic_phrases:
                            st.markdown(f"- <span style='color:#128c7e'>**Frequent topics:**</span> {', '.join(topic_phrases)}", unsafe_allow_html=True)
                    except Exception as e:
                        st.warning(f"Could not summarize human characteristics: {e}")
                except Exception as e:
                    st.warning(f"Could not summarize chatter details: {e}")
        except Exception as e:
            st.error(f"Failed to parse chat file: {e}")
    else:
        st.warning("No valid .txt file to analyze.")
else:
    st.warning("Upload a WhatsApp chat .txt or .zip file to get started.")
