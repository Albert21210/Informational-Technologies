import sqlite3
import pandas as pd
import os

def run_university_project():
    folder_name = "database_exports"
    db_name = "university_base.db"
    
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS positions (
        id_pos INTEGER PRIMARY KEY NOT NULL UNIQUE,
        name TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS employees (
        id_emp INTEGER PRIMARY KEY NOT NULL UNIQUE,
        surname TEXT NOT NULL,
        name TEXT NOT NULL,
        phone TEXT,
        id_pos INTEGER NOT NULL,
        FOREIGN KEY (id_pos) REFERENCES positions (id_pos)
    );
    CREATE TABLE IF NOT EXISTS clients (
        id_client INTEGER PRIMARY KEY NOT NULL UNIQUE,
        organization TEXT NOT NULL,
        phone TEXT
    );
    CREATE TABLE IF NOT EXISTS orders (
        id_order INTEGER PRIMARY KEY NOT NULL UNIQUE,
        id_client INTEGER NOT NULL,
        id_emp INTEGER NOT NULL,
        amount REAL NOT NULL,
        completion_date TEXT,
        is_completed INTEGER DEFAULT 0,
        FOREIGN KEY (id_client) REFERENCES clients (id_client),
        FOREIGN KEY (id_emp) REFERENCES employees (id_emp)
    );
    """)

    positions_data = [(1, 'Менеджер'), (2, 'Разработчик'), (3, 'Аналитик'), (4, 'Дизайнер')]
    cursor.executemany("INSERT OR IGNORE INTO positions VALUES (?,?)", positions_data)

    employees_data = [
        (1, 'Иванов', 'Иван', '8900111', 2),
        (2, 'Петров', 'Петр', '8900222', 1),
        (3, 'Сидорова', 'Мария', '8900333', 3),
        (4, 'Козлов', 'Алексей', '8900444', 2),
        (5, 'Васильева', 'Ольга', '8900555', 4)
    ]
    cursor.executemany("INSERT OR IGNORE INTO employees VALUES (?,?,?,?,?)", employees_data)

    clients_data = [(1, 'ТехноПром', '555-01'), (2, 'МедиаСофт', '555-02'), (3, 'Global IT', '555-03')]
    cursor.executemany("INSERT OR IGNORE INTO clients VALUES (?,?,?)", clients_data)

    orders_data = [
        (1, 1, 2, 50000.0, '2026-03-20', 1),
        (2, 2, 1, 15000.0, '2026-04-01', 0),
        (3, 3, 4, 120000.0, '2026-05-15', 0),
        (4, 1, 1, 3500.0, '2026-03-25', 1)
    ]
    cursor.executemany("INSERT OR IGNORE INTO orders VALUES (?,?,?,?,?,?)", orders_data)
    conn.commit()

    def print_query(title, query):
        print(f"\n{'='*50}\n{title}\n{'-'*50}")
        df = pd.read_sql_query(query, conn)
        print(df.to_string(index=False))
        return df

    # Пять простых запросов (агрегация)
    print("\n>>> ПЯТЬ ПРОСТЫХ ЗАПРОСОВ (АГРЕГАТЫ)")
    cursor.execute("SELECT COUNT(*) FROM employees")
    print(f"1. Кол-во сотрудников: {cursor.fetchone()[0]}")
    cursor.execute("SELECT MAX(amount) FROM orders")
    print(f"2. Максимальный заказ: {cursor.fetchone()[0]}")
    cursor.execute("SELECT SUM(amount) FROM orders")
    print(f"3. Общая сумма заказов: {cursor.fetchone()[0]}")
    cursor.execute("SELECT AVG(amount) FROM orders")
    print(f"4. Средний чек: {cursor.fetchone()[0]:.2f}")
    cursor.execute("SELECT MIN(amount) FROM orders")
    print(f"5. Минимальный заказ: {cursor.fetchone()[0]}")

    # Три запроса с агрегацией 
    print_query("КОЛИЧЕСТВО СОТРУДНИКОВ ПО ДОЛЖНОСТЯМ", 
                "SELECT id_pos, COUNT(*) as count FROM employees GROUP BY id_pos")
    
    print_query("СУММА ЗАКАЗОВ ПО КЛИЕНТАМ", 
                "SELECT id_client, SUM(amount) as total FROM orders GROUP BY id_client")
    
    print_query("СТАТУС ВЫПОЛНЕНИЯ ЗАКАЗОВ (0-НЕТ, 1-ДА)", 
                "SELECT is_completed, COUNT(*) as count FROM orders GROUP BY is_completed")

    # Три запроса с объединением (JOIN) 
    print_query("СПИСОК СОТРУДНИКОВ И ИХ ДОЛЖНОСТЕЙ", 
                "SELECT e.surname, e.name, p.name as position FROM employees e JOIN positions p ON e.id_pos = p.id_pos")
    
    print_query("ЗАКАЗЫ И ОРГАНИЗАЦИИ (СУММА > 10000)", 
                "SELECT c.organization, o.amount FROM orders o JOIN clients c ON o.id_client = c.id_client WHERE o.amount > 10000")
    
    print_query("РАЗРАБОТЧИКИ С ЗАКАЗАМИ", 
                "SELECT DISTINCT e.surname, p.name FROM employees e JOIN positions p ON e.id_pos = p.id_pos JOIN orders o ON e.id_emp = o.id_emp WHERE p.name = 'Разработчик'")

    print(f"\n{'*'*50}\nДанные сохранены в папке '{folder_name}'\n{'*'*50}")
    tables = ['positions', 'employees', 'clients', 'orders']
    for table in tables:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        path = os.path.join(folder_name, f"{table}.csv")
        df.to_csv(path, index=False, encoding='utf-8-sig')

    conn.close()

if __name__ == "__main__":
    run_university_project()