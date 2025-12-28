# 🔍 Text-to-SQL LLM Application

An end-to-end **LLM-powered Text-to-SQL application** that converts natural language questions into safe SQL queries, executes them on a real SQLite database, and displays results through an interactive Streamlit UI.

This project is designed to help **SQL beginners and data analytics learners** query databases using plain English while also learning real SQL.

---

## 🚀 Features

- 🔹 Natural Language → SQL using LLM
- 🔹 Safe SQL execution (SELECT-only)
- 🔹 Editable SQL with re-run support
- 🔹 Beginner & Advanced learning modes
- 🔹 Query execution time & row count
- 🔹 Auto visualizations (bar charts)
- 🔹 Export results (CSV, Excel, JSON)
- 🔹 Query history tracking

---

## 🛠 Tech Stack

- **Python**
- **Streamlit** (Frontend)
- **OpenAI API** (LLM)
- **SQLite** (Database)
- **Pandas** (Data handling)

---

## 📂 Project Structure
```
text-to-sql-llm-app/
├── app.py
├── app_core.py
├── generate_demo_db.py
├── sales.db
├── requirements.txt
├── .gitignore
└── screenshots/
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/text-to-sql-llm-app.git
cd text-to-sql-llm-app
```
### 2️⃣ Create & activate virtual environment
```
python -m venv venv
```
#### Windows
```
venv\Scripts\activate
```
#### Mac/Linux
```
source venv/bin/activate
```
