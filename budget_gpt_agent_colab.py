
# 🔧 שלב 1: התקנת ספריות
!pip install ipywidgets openai

# 🔧 שלב 2: ייבוא ספריות
import pandas as pd
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output
import openai
from google.colab import files
import datetime
import getpass

# 🔐 שלב 3: קבלת מפתח API
openai.api_key = getpass.getpass("🔐 הזיני את מפתח ה-API שלך כאן:")

# 📂 שלב 4: העלאת קובץ CSV
uploaded = files.upload()
file_path = list(uploaded.keys())[0]

# 📊 שלב 5: חישוב אחוז ביצוע
def calculate_budget_performance(file_path):
    df = pd.read_csv(file_path)
    df["אחוז ביצוע (%)"] = (df["הוצאה בפועל"] / df["תקציב"]) * 100
    return df

try:
    df = calculate_budget_performance(file_path)
except Exception as e:
    df = pd.DataFrame()
    print("שגיאה בטעינת הקובץ:", e)

# ✏️ שלב 6: תקציר ל-GPT
def summarize_table_for_gpt(df, max_rows=10):
    summary = df.copy()
    if "אחוז ביצוע (%)" in summary.columns:
        summary = summary.sort_values("אחוז ביצוע (%)", ascending=False)
    return summary.head(max_rows).to_string(index=False)

# 🧠 שלב 7: זיכרון שיחה
conversation_memory = []

# 💬 שלב 8: שיחה עם GPT כולל הקשר
def ask_gpt_with_memory(question, df):
    global conversation_memory
    if not conversation_memory:
        context = summarize_table_for_gpt(df)
        system_message = {
            "role": "system",
            "content": (
                "אתה עוזר לנתח תקציב של ארגון. הטבלה כוללת שמות מחלקות, תקציב, ביצוע בפועל ואחוז ביצוע. "
                f"ענה בצורה תמציתית, מדויקת וברורה.
הנה התקציר:
{context}"
            )
        }
        conversation_memory.append(system_message)

    conversation_memory.append({"role": "user", "content": question})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation_memory
    )
    answer = response.choices[0].message.content.strip()
    conversation_memory.append({"role": "assistant", "content": answer})
    return answer

# 📈 שלב 9: פונקציות ניתוח נוספות
def get_underperforming_departments(df):
    return df[df["אחוז ביצוע (%)"] < 80]

def get_highest_budget_department(df):
    return df[df["תקציב"] == df["תקציב"].max()]

def summarize_budget_by_category(df):
    return df.groupby("קטגוריה")["תקציב"].sum().reset_index()

def plot_performance_chart(df):
    plt.figure(figsize=(10, 5))
    plt.bar(df["מחלקה"], df["אחוז ביצוע (%)"], color='skyblue')
    plt.xticks(rotation=45, ha='right')
    plt.ylabel("אחוז ביצוע (%)")
    plt.title("אחוז ביצוע לפי מחלקה")
    plt.tight_layout()
    plt.show()
    return "גרף מוצג למעלה."

# 🗺️ שלב 10: מיפוי שאלות נפוצות
question_map = {
    "מי חרג מהתקציב?": lambda df: df[df["אחוז ביצוע (%)"] > 100],
    "מי ביצע פחות מ־80%?": get_underperforming_departments,
    "מי קיבל את התקציב הגבוה ביותר?": get_highest_budget_department,
    "מה סך התקציב לפי קטגוריות?": summarize_budget_by_category,
    "הצג טבלה": lambda df: df.to_string(index=False),
    "הצג גרף עמודות המראה את אחוז ביצוע לכל מחלקה": lambda df: plot_performance_chart(df)
}

# 🧰 שלב 11: ממשק משתמש
question_input = widgets.Text(placeholder='הכנס שאלה על התקציב כאן', description='שאלה:', layout=widgets.Layout(width='70%'))
ask_button = widgets.Button(description="שאל את הסוכן", button_style='primary')
reset_button = widgets.Button(description="איפוס שיחה")
upload_button = widgets.Button(description="העלה קובץ חדש")
save_button = widgets.Button(description="📄 שמור שיחה כ-TXT")
save_csv_button = widgets.Button(description="💾 שמור כ-CSV")
info_label = widgets.Label(value="💡 ניתן לשאול שאלות כמו: 'מי חרג מהתקציב?' או 'מה אחוז ביצוע לכל מחלקה?'")
privacy_label = widgets.Label(value="🔐 המידע נשמר מקומית בלבד.")
output_area = widgets.Output()

# 🔘 שלב 12: פעולות כפתורים
def on_ask_clicked(b):
    with output_area:
        clear_output()
        if df.empty:
            print("⚠️ לא נטען קובץ תקין. נא להעלות קובץ מחדש.")
            return
        question = question_input.value.strip()
        if question:
            if question in question_map:
                result = question_map[question](df)
                print(result)
            elif "גרף" in question:
                print(plot_performance_chart(df))
            else:
                print("▶ תשובת הסוכן:")
                print(ask_gpt_with_memory(question, df))
        else:
            print("אנא הקלד שאלה.")

def on_reset_clicked(b):
    global conversation_memory
    question_input.value = ''
    conversation_memory = []
    with output_area:
        clear_output()
        print("🔄 הזיכרון אופס. אפשר להתחיל שיחה חדשה.")

def on_upload_clicked(b):
    global df
    with output_area:
        clear_output()
        print("📂 בחר קובץ חדש...")
        uploaded = files.upload()
        file_path = list(uploaded.keys())[0]
        try:
            df = calculate_budget_performance(file_path)
            print("✅ קובץ נטען בהצלחה!")
        except Exception as e:
            df = pd.DataFrame()
            print("❌ שגיאה בטעינת הקובץ:", e)

def on_save_clicked(b):
    with open("chat_log.txt", "w", encoding="utf-8") as f:
        f.write("שיחה עם הסוכן – " + str(datetime.datetime.now()) + "\n\n")
        for m in conversation_memory:
            if m['role'] != 'system':
                prefix = "שאלה" if m['role'] == 'user' else "תשובה"
                f.write(f"{prefix}: {m['content']}\n\n")
    files.download("chat_log.txt")

def on_save_csv_clicked(b):
    rows = []
    for i in range(0, len(conversation_memory)):
        if conversation_memory[i]['role'] == 'user' and i+1 < len(conversation_memory):
            user_q = conversation_memory[i]['content']
            if conversation_memory[i+1]['role'] == 'assistant':
                assistant_a = conversation_memory[i+1]['content']
                rows.append((user_q, assistant_a))
    df_chat = pd.DataFrame(rows, columns=['שאלה', 'תשובה'])
    df_chat.to_csv("chat_log.csv", index=False, encoding='utf-8-sig')
    files.download("chat_log.csv")

ask_button.on_click(on_ask_clicked)
reset_button.on_click(on_reset_clicked)
upload_button.on_click(on_upload_clicked)
save_button.on_click(on_save_clicked)
save_csv_button.on_click(on_save_csv_clicked)

# 📺 שלב 13: הצגת הממשק
display(widgets.VBox([
    question_input,
    widgets.HBox([ask_button, reset_button, upload_button, save_button, save_csv_button]),
    info_label,
    privacy_label,
    output_area
]))
