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
### 3️⃣ Install dependencies
```
pip install -r requirements.txt
```
### 4️⃣ Set OpenAI API key

Create a .env file:
```
OPENAI_API_KEY=your_api_key_here
```
### 5️⃣ Generate demo database
```
python generate_demo_db.py
```
### 6️⃣ Run the app
```
streamlit run app.py
```
## 💡 Example Questions

- Total revenue by city
- Show sales from Bengaluru
- Average price of each product
- Total quantity sold per product

## 🎯 Learning Objective

This project helps beginners:

- Understand how SQL queries are structured
- Learn JOINs, GROUP BY, and filters
- See how AI can assist in data analysis

## 📌 Future Enhancements

- Multi-database support (MySQL, PostgreSQL)
- Voice-to-SQL
- SQL optimization suggestions
- User authentication

## 👤 Author

**Manthan Patel**
- Linkedin: [Manthan Patel](https://www.linkedin.com/in/manthan-patel18)
- Portfolio: [yourwebsite.com](https://yourwebsite.com)
