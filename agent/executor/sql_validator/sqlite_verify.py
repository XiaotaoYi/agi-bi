import sqlite3
from typing import Optional

def parse_sql(sql: str) -> bool:
    """
    Validate SQL syntax by attempting to prepare the statement
    :param sql: SQL statement to validate
    :return: True if valid, False otherwise
    """
    try:
        # Create an in-memory database for validation
        conn = sqlite3.connect('tools/sql_executor/order.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(f"EXPLAIN {sql}")
        return True
    except sqlite3.Error as e:
        print(e)
        return False
    finally:
        if 'conn' in locals():
            conn.close() 