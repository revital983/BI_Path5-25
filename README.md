
# 📊 סוכן תקציב חכם - Budget Chatbot

אפליקציית Streamlit חכמה לניתוח קבצי תקציב בשפה טבעית בעזרת GPT.

## 📂 קבצים בפרויקט:
- `budget_gpt_agent_colab.py` – הקוד הראשי
- `.streamlit/secrets.toml` – מפתח OpenAI
- `README.md` – הוראות שימוש

## 🚀 איך להריץ מקומית:
```bash
pip install streamlit openai pandas
streamlit run app.py
```

## 🌐 איך להפעיל ב־Streamlit Cloud:
1. העלה את התיקייה ל־GitHub
2. עבור ל־https://streamlit.io/cloud
3. התחבר → לחצן `New app`
4. בחר את הריפו → קובץ `app.py`
5. הקלד את מפתח ה־API ב־Secrets
