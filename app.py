# app.py – אפליקציית Streamlit לבוט תקציב עם ChatGPT

import streamlit as st
import pandas as pd
import openai
import io

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="סוכן תקציב חכם", page_icon="📊")
st.title("📊 סוכן חכם לניתוח תקציב")
st.markdown("העלה קובץ תקציב, שאל שאלה וקבל תשובה מ־GPT כולל גרפים וטבלאות ✨")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

uploaded_file = st.file_uploader("העלה קובץ CSV של תקציב:", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df["אחוז ביצוע (%)"] = (df["הוצאה בפועל"] / df["תקציב"]) * 100

    with st.expander("📋 הצג טבלת תקציב מלאה"):
        st.dataframe(df)

    if st.checkbox("📈 הצג גרף ביצועים"):
        st.bar_chart(df.set_index("מחלקה")["אחוז ביצוע (%)"])

    question = st.text_input("🔎 שאל שאלה על התקציב:")

    def summarize_table(df, max_rows=10):
        summary = df[["מחלקה", "תקציב", "הוצאה בפועל", "אחוז ביצוע (%)"]].copy()
        summary = summary.sort_values("אחוז ביצוע (%)", ascending=False)
        summary = summary.head(max_rows)
        return summary.to_markdown(index=False)

    def ask_gpt_with_context(question, df):
        context = summarize_table(df)
        system = (
            "אתה עוזר לנתח תקציב של ארגון. "
            "ענה בעברית בצורה תמציתית, אם רלוונטי הצג טבלה פשוטה בעברית עם עמודות.\n\n"
            f"הנה טבלה מסוכמת:\n{context}"
        )
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": question}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response.choices[0].message.content.strip()

    if question:
        with st.spinner("GPT חושב..."):
            answer = ask_gpt_with_context(question, df)
            st.session_state.chat_history.append((question, answer))

    if st.session_state.chat_history:
        st.markdown("---")
        st.markdown("### 💬 שיחה עם הסוכן")
        for q, a in reversed(st.session_state.chat_history):
            st.markdown(f"**שאלה:** {q}")
            st.markdown(f"**תשובה:** {a}")
else:
    st.info("נא להעלות קובץ CSV על מנת להתחיל")
