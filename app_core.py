# app_core.py
"""
App core for Text -> SQL application (OpenAI v2.x compatible)
- Generates SQL from natural language using OpenAI
- Explains SQL using OpenAI
- Runs SQL safely on local SQLite DB (sales.db)
- Contains small auto-join fixer and schema-aware prompt
"""

import os
import sqlite3
import pandas as pd
import re
from openai import OpenAI
from dotenv import load_dotenv

# Load .env
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise Exception("OPENAI_API_KEY not found in environment. Please set it in .env file.")

# Initialize OpenAI client
client = OpenAI(api_key=API_KEY)

DB_PATH = "sales.db"

# ---- Database schema reference (explicit) ----
# We give this to the LLM so it doesn't invent wrong column names like products.name or products.id
SCHEMA_NOTE = """
Database schema (use these exact names):

TABLE products:
 - product_id  (INTEGER)   -- primary key
 - product_name (TEXT)
 - category (TEXT)

TABLE customers:
 - customer_id (INTEGER)   -- primary key
 - name (TEXT)
 - city (TEXT)

TABLE sales:
 - id (INTEGER)            -- primary key
 - date (TEXT)             -- format YYYY-MM-DD
 - product_id (INTEGER)    -- foreign key -> products.product_id
 - customer_id (INTEGER)   -- foreign key -> customers.customer_id
 - quantity (INTEGER)
 - price (REAL)
"""

# ---- Helpers ----
def _clean_model_sql(raw: str) -> str:
    """
    Remove markdown fences and extraneous commentary from model output.
    """
    if not raw:
        return raw
    sql = raw.strip()
    # Remove triple backticks (```sql or ``` or ```text)
    sql = re.sub(r"```(?:sql)?", "", sql, flags=re.IGNORECASE).strip()
    # If model returned explanation followed by SQL, try to extract the longest SQL-looking substring
    # A naive approach: find first "SELECT" and take until the last semicolon (if exists) or end.
    m = re.search(r"(?i)(select\b.*)", sql, flags=re.DOTALL)
    if m:
        candidate = m.group(1).strip()
        # If there are multiple statements, keep everything up to last semicolon (or entire string).
        # But we will only allow SELECT statements in safety check anyway.
        return candidate
    return sql

def _auto_fix_joins(sql: str) -> str:
    """
    If the LLM produced a query referencing sales but didn't include JOINs for product_name/customer name,
    add appropriate LEFT JOINs. This is a heuristic only.
    """
    sql_lower = sql.lower()
    if "from sales" in sql_lower and ("product_name" in sql_lower or "customer_name" in sql_lower or "customers.name" in sql_lower):
        # If joins already present, return as is
        if "join products" in sql_lower or "join customers" in sql_lower:
            return sql
        # Add LEFT JOINs to map product_id -> product_name and customer_id -> name
        # We attempt to inject joins after the FROM clause. This is a simple safe approach.
        pattern = re.compile(r'from\s+sales\b', flags=re.IGNORECASE)
        replacement = (
            "FROM sales s\nLEFT JOIN products p ON s.product_id = p.product_id\nLEFT JOIN customers c ON s.customer_id = c.customer_id"
        )
        fixed_sql = pattern.sub(replacement, sql, count=1)
        return fixed_sql
    return sql

# ---- Safety check ----
def is_sql_safe(sql: str) -> bool:
    """
    Allow only SELECT queries. Block any DDL/DML or dangerous characters.
    """
    if not sql:
        return False
    sql_lower = sql.strip().lower()
    # Disallow statements other than select
    if not sql_lower.startswith("select"):
        return False
    # Block common dangerous keywords or multiple statements
    forbidden = ["insert", "update", "delete", "drop", "alter", "create", "attach", "pragma", "vacuum", ";--", "--"]
    if any(token in sql_lower for token in forbidden):
        return False
    # Prevent multiple statements separated by semicolon
    if ";" in sql_lower and sql_lower.count(";") > 1:
        return False
    # If semicolon exists, ensure it is at end only (still be cautious)
    return True

# ---- LLM -> SQL generation ----
def generate_sql_from_text(question: str, model="gpt-4o-mini", max_tokens: int = 300) -> str:
    """
    Generate a SQLite SELECT SQL query from a natural language question.
    This function provides a strong system prompt with the exact schema and rules.
    """
    # Build a careful prompt with explicit rules
    system_msg = (
        "You are an expert SQL generator for SQLite databases. "
        "You must follow instructions strictly and only output a single valid SQL SELECT statement (no explanation). "
        "Do NOT return any commentary. Do NOT use backticks. Use the exact table and column names provided."
    )

    user_msg = f"""
{SCHEMA_NOTE}

Important rules for generation:
- Output ONLY one SELECT SQL statement. Do NOT output explanation or text.
- Use the exact column names from the schema above:
  - product_name is products.product_name (NOT products.name)
  - product primary key is products.product_id
  - customer name is customers.name (NOT customers.customer_name)
  - customer primary key is customers.customer_id
  - sale price is in sales.price (NOT products.price)
  - join using sales.product_id = products.product_id and sales.customer_id = customers.customer_id
- If the question requests product name or customer name, include JOINs to products and customers.
- Use table aliases s (sales), p (products), c (customers) when helpful.
- Only use SQLite-compatible functions.
- Avoid speculative column names. If unsure, prefer columns present in the schema.

User question:
\"\"\"{question}\"\"\"
"""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=max_tokens,
            temperature=0.0,
        )
        raw = resp.choices[0].message.content
    except Exception as e:
        # Bubble up exception to caller (app.py will handle and display)
        raise Exception(f"OpenAI API error: {e}")

    sql = _clean_model_sql(raw)
    # Try to auto-fix missing joins if model forgot to add them
    sql = _auto_fix_joins(sql)
    return sql

# ---- LLM-based explanation ----
def explain_sql(sql: str, model="gpt-4o-mini", max_tokens: int = 200) -> str:
    """
    Ask the model to explain the SQL in simple English.
    """
    prompt = f"Explain this SQL query in simple plain English in 2-3 sentences. SQL:\n\n{sql}"
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.0,
        )
        expl = resp.choices[0].message.content.strip()
        return expl
    except Exception as e:
        return f"(Explanation failed: {e})"

# ---- Execute SQL on SQLite ----
def run_sql(sql: str) -> pd.DataFrame:
    """
    Run the SQL on local SQLite DB (DB_PATH) and return a pandas DataFrame.
    """
    if not is_sql_safe(sql):
        raise Exception("SQL blocked by safety policy (only SELECT allowed or query contained unsafe tokens).")

    # Clean trailing semicolons if present (pandas.read_sql_query can accept them but keep consistent)
    sql_to_run = sql.strip().rstrip(";")

    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(sql_to_run, conn)
    except Exception as e:
        # Provide helpful error with original SQL
        conn.close()
        raise Exception(f"SQL execution error: {e}")
    conn.close()
    return df

# ---- Optional: utility to get DB schema at runtime ----
def get_db_schema() -> dict:
    """
    Inspect the SQLite DB and return a dict: {table_name: [column1, column2, ...]}
    Useful for debugging and UI schema display.
    """
    schema = {}
    if not os.path.exists(DB_PATH):
        return schema
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]
        for t in tables:
            cur.execute(f"PRAGMA table_info({t});")
            cols = [r[1] for r in cur.fetchall()]
            schema[t] = cols
    finally:
        conn.close()
    return schema
