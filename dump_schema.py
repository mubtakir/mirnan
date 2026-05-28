import sqlite3
import sys

def dump_schema(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for name, sql in tables:
        print(f"Table: {name}")
        print(f"Schema: {sql}")
        
        # Get one sample row to see data
        try:
            cursor.execute(f"SELECT * FROM {name} LIMIT 1")
            row = cursor.fetchone()
            if row:
                col_names = [description[0] for description in cursor.description]
                print(f"Sample row: {dict(zip(col_names, row))}")
            else:
                print("Sample row: (empty table)")
        except Exception as e:
            print(f"Error querying table {name}: {e}")
        print("-" * 50)
        
    conn.close()

if __name__ == '__main__':
    dump_schema('arabic_tools/arramooz/arramooz.db')
