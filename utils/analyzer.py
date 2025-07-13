import pandas as pd
import streamlit as st
import plotly.express as px

def generate_statistics(df):
    stats = {
        "Total Messages": len(df),
        "Participants": df['sender'].nunique(),
        "Top Chatter": df['sender'].value_counts().idxmax(),
        "Most Active Day": df['weekday'].value_counts().idxmax(),
        "Most Active Hour": df['hour'].value_counts().idxmax()
    }
    return stats

def plot_charts(df):
    fig1 = px.histogram(df, x="sender", title="Messages per Sender", color="sender")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.histogram(df, x="hour", nbins=24, title="Activity by Hour")
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.histogram(df, x="weekday", title="Activity by Weekday", category_orders={"weekday": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]})
    st.plotly_chart(fig3, use_container_width=True)
