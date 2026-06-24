# --- Imports ---
import pandas as pd
import streamlit as st
from textblob import TextBlob
import plotly.express as px
import anthropic
import json

# --- Page title ---
st.title("Sentiment Analysis Dashboard")
st.write("Upload a CSV file with reviews to analyze sentiment.")

# --- Initialize session state ---
if "df_results" not in st.session_state:
    st.session_state.df_results = None
if "review_col" not in st.session_state:
    st.session_state.review_col = None

# --- File uploader ---
file = st.file_uploader("Upload your CSV file", type=["csv"])

if file is not None:

    # Read the CSV
    df = pd.read_csv(file, quotechar='"', engine='python')
    st.success("File uploaded successfully!")
    st.dataframe(df)

    # --- Column selector ---
    text_columns = df.select_dtypes(include=["object"]).columns.tolist()
    review_col = st.selectbox("Select the column with reviews", options=text_columns)
    st.write(f"Total reviews: {len(df)}")

    # --- Analyze button --- (inside if file is not None)
    if st.button("Analyze Sentiment"):
        try:
            with st.spinner("Analyzing reviews..."):

                # TextBlob analysis
                def get_textblob_sentiment(text):
                    analysis = TextBlob(str(text))
                    polarity = analysis.sentiment.polarity
                    if polarity > 0.1:
                        return "Positive", round(polarity, 2)
                    elif polarity < -0.1:
                        return "Negative", round(polarity, 2)
                    else:
                        return "Neutral", round(polarity, 2)

                df[["Sentiment", "Score"]] = df[review_col].apply(
                    lambda x: pd.Series(get_textblob_sentiment(x))
                )

                # Save results to session state
                st.session_state.df_results = df.copy()
                st.session_state.review_col = review_col
                st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")

# --- Show results if they exist in session state ---
if st.session_state.df_results is not None:
    df = st.session_state.df_results
    review_col = st.session_state.review_col

    st.success("Basic analysis complete!")

    # --- Results table ---
    st.subheader("Results — TextBlob Analysis")
    st.dataframe(df[[review_col, "Sentiment", "Score"]])

    # --- Pie chart ---
    st.subheader("Sentiment Distribution")
    fig_pie = px.pie(
        df, names="Sentiment", color="Sentiment",
        color_discrete_map={"Positive": "#2E86AB", "Neutral": "#F0A500", "Negative": "#E63946"},
        title="Overall Sentiment"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # --- Bar chart ---
    st.subheader("Score Distribution")
    fig_bar = px.histogram(
        df, x="Score", color="Sentiment",
        color_discrete_map={"Positive": "#2E86AB", "Neutral": "#F0A500", "Negative": "#E63946"},
        nbins=20, title="Polarity Score Distribution"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- Summary metrics ---
    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)
    counts = df["Sentiment"].value_counts()
    with col1:
        st.metric("Positive", counts.get("Positive", 0))
    with col2:
        st.metric("Neutral", counts.get("Neutral", 0))
    with col3:
        st.metric("Negative", counts.get("Negative", 0))

    # --- Divider ---
    st.divider()

    # --- Claude API section ---
    st.subheader("🔑 Advanced AI Analysis — Claude")
    st.write("For a deeper contextual analysis, enter your Anthropic API key below.")
    st.caption("Your key is never stored and is only used during this session.")

    user_api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")

    if user_api_key:
        if st.button("Run Claude AI Analysis"):
            with st.spinner("Running Claude AI analysis..."):

                client = anthropic.Anthropic(api_key=user_api_key)

                def get_claude_sentiment(text):
                    message = client.messages.create(
                        model="claude-sonnet-4-6",
                        max_tokens=100,
                        messages=[
                            {
                                "role": "user",
                                "content": f"""Analyze the sentiment of this review and respond with ONLY a JSON object like this:
{{"sentiment": "Positive/Negative/Neutral", "score": 0.0, "reason": "brief explanation"}}

Review: {text}"""
                            }
                        ]
                    )
                    response = json.loads(message.content[0].text)
                    return response["sentiment"], response["score"], response["reason"]

                df[["Claude Sentiment", "Claude Score", "Claude Reason"]] = df[review_col].apply(
                    lambda x: pd.Series(get_claude_sentiment(x))
                )

                st.session_state.df_results = df.copy()
                st.rerun()

        # --- Show Claude results if they exist ---
        if "Claude Sentiment" in st.session_state.df_results.columns:
            df = st.session_state.df_results

            st.success("Claude AI analysis complete!")
            st.subheader("TextBlob vs Claude AI")
            st.dataframe(df[[review_col, "Sentiment", "Score", "Claude Sentiment", "Claude Score", "Claude Reason"]])

            col1, col2 = st.columns(2)
            with col1:
                fig1 = px.pie(df, names="Sentiment", title="TextBlob",
                    color="Sentiment",
                    color_discrete_map={"Positive": "#2E86AB", "Neutral": "#F0A500", "Negative": "#E63946"})
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                fig2 = px.pie(df, names="Claude Sentiment", title="Claude AI",
                    color="Claude Sentiment",
                    color_discrete_map={"Positive": "#2E86AB", "Neutral": "#F0A500", "Negative": "#E63946"})
                st.plotly_chart(fig2, use_container_width=True)