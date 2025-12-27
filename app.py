import streamlit as st
import pandas as pd
import time
import io

from app_core import (
    generate_sql_from_text,
    is_sql_safe,
    explain_sql,
    run_sql,
)

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Natural Language → SQL Demo",
    layout="wide"
)

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "generated_sql" not in st.session_state:
    st.session_state.generated_sql = ""

if "query_result" not in st.session_state:
    st.session_state.query_result = None

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------
st.title("🔍 Natural Language → SQL Demo")
st.write(
    "Ask a question about the sales database. "
    "The app generates SQL, executes it, and explains the result."
)

# ---------------------------------------------------
# LEARNING MODE TOGGLE
# ---------------------------------------------------
st.markdown("### 🎓 Learning Mode")

learning_mode = st.toggle(
    "Beginner Mode (Read-only SQL)",
    value=True
)

if learning_mode:
    st.info(
        "🔒 Beginner Mode ON: SQL is read-only. "
        "Switch OFF to edit and re-run SQL."
    )
else:
    st.success(
        "🛠 Advanced Mode ON: You can edit and re-run SQL."
    )

# ---------------------------------------------------
# EXAMPLE QUESTIONS
# ---------------------------------------------------
with st.expander("💡 Try example questions"):
    examples = [
        "Total quantity sold per product",
        "Show sales from Bengaluru",
        "Total revenue by city",
        "Average price of each product",
    ]
    cols = st.columns(4)
    for i, q in enumerate(examples):
        if cols[i % 4].button(q):
            st.session_state.example_question = q

# ---------------------------------------------------
# DATABASE SCHEMA
# ---------------------------------------------------
with st.expander("📦 View Database Schema"):
    st.markdown("""
**sales**
- id
- date
- product_id
- customer_id
- quantity
- price

**products**
- product_id
- product_name
- category

**customers**
- customer_id
- name
- city
""")

# ---------------------------------------------------
# INPUT
# ---------------------------------------------------
question = st.text_input(
    "Enter your question",
    value=st.session_state.get("example_question", "")
)

col1, col2 = st.columns([1, 0.2])
with col1:
    generate_btn = st.button("Generate & Run SQL")
with col2:
    if st.button("Clear History"):
        st.session_state.history = []
        st.success("History cleared")

# ---------------------------------------------------
# GENERATE SQL
# ---------------------------------------------------
if generate_btn:
    if not question.strip():
        st.warning("Please enter a question")
        st.stop()

    with st.spinner("Generating SQL..."):
        sql = generate_sql_from_text(question)

    st.session_state.generated_sql = sql

# ---------------------------------------------------
# SQL DISPLAY (READ-ONLY / EDITABLE)
# ---------------------------------------------------
if st.session_state.generated_sql:

    st.subheader("Generated SQL")

    if learning_mode:
        st.code(st.session_state.generated_sql, language="sql")
        run_sql_text = st.session_state.generated_sql
        run_now = True
    else:
        edited_sql = st.text_area(
            "Edit SQL and click Run SQL",
            value=st.session_state.generated_sql,
            height=120
        )
        run_now = st.button("▶ Run SQL")
        run_sql_text = edited_sql

    # ---------------------------------------------------
    # RUN SQL
    # ---------------------------------------------------
    if run_now:

        if not is_sql_safe(run_sql_text):
            st.error("Unsafe SQL detected. Only SELECT queries are allowed.")
            st.stop()

        start_time = time.time()
        try:
            df = run_sql(run_sql_text)
        except Exception as e:
            st.error(f"SQL Error: {e}")
            st.stop()

        exec_time = round(time.time() - start_time, 4)

        st.success("✅ Query executed successfully")
        st.info(f"📊 Rows returned: {len(df)} | ⏱ Time: {exec_time}s")

        st.session_state.query_result = df

        # ---------------------------------------------------
        # EXPLANATION
        # ---------------------------------------------------
        st.subheader("Explanation (Plain English)")
        explanation = explain_sql(run_sql_text)
        st.info(explanation)

        # ---------------------------------------------------
        # RESULTS
        # ---------------------------------------------------
        if df.empty:
            st.warning("Query returned 0 rows")
        else:
            st.subheader("Query Results")
            st.dataframe(df)

            # ---------------------------------------------------
            # AUTO CHART
            # ---------------------------------------------------
            numeric_cols = df.select_dtypes(include="number").columns
            object_cols = df.select_dtypes(include="object").columns

            if len(numeric_cols) and len(object_cols):
                st.subheader("Auto Chart")
                chart_df = df.groupby(object_cols[0])[numeric_cols[0]].sum()
                st.bar_chart(chart_df)

            # ---------------------------------------------------
            # EXPORT
            # ---------------------------------------------------
            st.subheader("⬇ Export Results")

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download CSV",
                csv,
                file_name="result.csv",
                mime="text/csv"
            )

            excel_buffer = io.BytesIO()
            df.to_excel(excel_buffer, index=False)
            st.download_button(
                "Download Excel",
                excel_buffer.getvalue(),
                file_name="result.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # ---------------------------------------------------
        # SAVE HISTORY
        # ---------------------------------------------------
        st.session_state.history.insert(0, {
            "question": question,
            "sql": run_sql_text,
            "rows": len(df),
            "time": exec_time
        })

# ---------------------------------------------------
# SIDEBAR HISTORY
# ---------------------------------------------------
st.sidebar.header("🔁 Query History")

if not st.session_state.history:
    st.sidebar.info("No history yet")
else:
    for item in st.session_state.history:
        with st.sidebar.expander(item["question"]):
            st.code(item["sql"], language="sql")
            st.write(f"Rows: {item['rows']} | Time: {item['time']}s")
