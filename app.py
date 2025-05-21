
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import openai
import io

# הגדרת מפתח API דרך secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="סוכן תקציב חכם", layout="wide")
st.title("🤖 סוכן GPT לניתוח קבצי תקציב")

# משתנים גלובליים
conversation_memory = []
df = pd.DataFrame()

# העלאת קובץ
uploaded_file = st.file_uploader("📂 העלה קובץ תקציב (CSV)", type=["csv"])
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df["אחוז ביצוע (%)"] = (df["הוצאה בפועל"] / df["תקציב"]) * 100
        st.success("✅ הקובץ נטען בהצלחה!")
        st.dataframe(df)
    except Exception as e:
        st.error(f"שגיאה בטעינת הקובץ: {e}")

# סיכום טבלה ל-GPT
def summarize_table_for_gpt(df, max_rows=10):
    summary = df.copy()
    if "אחוז ביצוע (%)" in summary.columns:
        summary = summary.sort_values("אחוז ביצוע (%)", ascending=False)
    return summary.head(max_rows).to_string(index=False)

# שליחת שאלה ל-GPT עם זיכרון
# יצירת client לפי הגרסה החדשה של openai
client = openai.Client()

def ask_gpt_with_memory(question, df):
    global conversation_memory

    if not conversation_memory:
        context = summarize_table_for_gpt(df)
        system_message = {
            "role": "system",
            "content": (
                f"אתה עוזר לנתח תקציב של ארגון. הטבלה כוללת שמות מחלקות, תקציב, ביצוע בפועל ואחוז ביצוע. "
                f"ענה בצורה תמציתית, מדויקת וברורה.\nהנה התקציר:\n{context}"
            )
        }
        conversation_memory.append(system_message)

    conversation_memory.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation_memory
    )
    answer = response.choices[0].message.content.strip()
    conversation_memory.append({"role": "assistant", "content": answer})
    return answer


# תצוגת שיחה
if not df.empty:
    with st.expander("💬 שוחח עם הסוכן", expanded=True):
        user_question = st.text_input("הקלד שאלה")
        if st.button("שאל"):
            if user_question:
                response = ask_gpt_with_memory(user_question, df)
                st.markdown("**🧠 תשובת הסוכן:**")
                st.write(response)
            else:
                st.warning("אנא הקלד שאלה.")

    # גרף ביצועים
    if st.button("📊 הצג גרף ביצועים"):
        try:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(df["מחלקה"], df["אחוז ביצוע (%)"], color='skyblue')
            ax.set_title("אחוז ביצוע לפי מחלקה")
            ax.set_ylabel("אחוז ביצוע (%)")
            ax.set_xticklabels(df["מחלקה"], rotation=45, ha='right')
            st.pyplot(fig)
        except:
            st.error("שגיאה ביצירת הגרף.")
