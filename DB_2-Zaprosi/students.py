import sqlite3
import pandas as pd
import os

report_dir = 'db_report'
if not os.path.exists(report_dir):
    os.makedirs(report_dir)
    print(f"Папка '{report_dir}' создана.")

conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

cursor.executescript('''
CREATE TABLE уровень_обучения (
    id_уровня INTEGER PRIMARY KEY,
    название VARCHAR(255)
);

CREATE TABLE направления (
    id_направления INTEGER PRIMARY KEY,
    название VARCHAR(255)
);

CREATE TABLE типы_обучения (
    id_типа INTEGER PRIMARY KEY,
    название VARCHAR(255)
);

CREATE TABLE студенты (
    id_студента INTEGER PRIMARY KEY,
    id_уровня INTEGER,
    id_направления INTEGER,
    id_типа_обучения INTEGER,
    фамилия VARCHAR(255),
    имя VARCHAR(255),
    отчество VARCHAR(255),
    средний_балл INTEGER,
    FOREIGN KEY (id_уровня) REFERENCES уровень_обучения(id_уровня),
    FOREIGN KEY (id_направления) REFERENCES направления(id_направления),
    FOREIGN KEY (id_типа_обучения) REFERENCES типы_обучения(id_типа)
);
''') 

cursor.execute("INSERT INTO уровень_обучения VALUES (1, 'Бакалавриат'), (2, 'Магистратура')")
cursor.execute("INSERT INTO направления VALUES (1, 'Прикладная Информатика'), (2, 'Экономика')")
cursor.execute("INSERT INTO типы_обучения VALUES (1, 'Очная'), (2, 'Вечерняя'), (3, 'Заочная')")

students_data = [
    (1, 1, 1, 1, 'Иванов', 'Иван', 'Иванович', 95),
    (2, 1, 1, 1, 'Иванов', 'Петр', 'Сидорович', 88),
    (3, 1, 1, 1, 'Петров', 'Иван', 'Иванович', 92),
    (4, 1, 2, 2, 'Сидоров', 'Алексей', 'Петрович', 75),
    (5, 1, 1, 1, 'Смирнов', 'Игорь', 'Олегович', 98),
    (6, 1, 1, 1, 'Кузнецов', 'Антон', 'Сергеевич', 91),
    (7, 1, 1, 1, 'Иванов', 'Иван', 'Иванович', 85),
    (8, 1, 1, 1, 'Иванов', 'Сергей', 'Павлович', 90)
]
cursor.executemany("INSERT INTO студенты VALUES (?, ?, ?, ?, ?, ?, ?, ?)", students_data)
conn.commit()

def process_data(title, filename, query):
    print("--- ", title, " ---")
    df = pd.read_sql_query(query, conn)
    
    path = os.path.join(report_dir, f"{filename}.csv")
    df.to_csv(path, index=False, encoding='utf-8-sig')
    
    print(df.to_string(index=False))

tables = ['уровень_обучения', 'направления', 'типы_обучения', 'студенты']
for table in tables:
    process_data(f"Таблица {table}", f"table_{table}", f"SELECT * FROM {table}")


# 1. Количество всех студентов 
process_data("1. Всего студентов", "query_1_total", 
             "SELECT COUNT(*) AS всего_студентов FROM студенты")

# 2. Студенты по направлениям 
process_data("2. По направлениям", "query_2_directions", 
             """SELECT n.название, COUNT(s.id_студента) AS кол_во 
                FROM студенты s JOIN направления n ON s.id_направления = n.id_направления 
                GROUP BY n.название""")

# 3. По формам обучения
process_data("3. По формам обучения", "query_3_forms", 
             """SELECT t.название, COUNT(s.id_студента) AS кол_во 
                FROM студенты s JOIN типы_обучения t ON s.id_типа_обучения = t.id_типа 
                GROUP BY t.название""")

# 4. Баллы по направлениям
process_data("4. Статистика баллов", "query_4_stats", 
             """SELECT n.название, MAX(s.средний_балл) AS макс, MIN(s.средний_балл) AS мин, AVG(s.средний_балл) AS средний 
                FROM студенты s JOIN направления n ON s.id_направления = n.id_направления 
                GROUP BY n.название""")

# 5. Детальный средний балл
process_data("5. Средний балл (детально)", "query_5_detailed_avg", 
             """SELECT n.название AS напр, u.название AS ур, t.название AS форма, AVG(s.средний_балл) AS балл 
                FROM студенты s 
                JOIN направления n ON s.id_направления = n.id_направления 
                JOIN уровень_обучения u ON s.id_уровня = u.id_уровня 
                JOIN типы_обучения t ON s.id_типа_обучения = t.id_типа 
                GROUP BY n.название, u.название, t.название""")

# 6. Топ-5 для стипендии 
process_data("6. Топ-5 Прикл. Информатика (Очная)", "query_6_top5", 
             """SELECT фамилия, имя, средний_балл FROM студенты s 
                JOIN направления n ON s.id_направления = n.id_направления 
                JOIN типы_обучения t ON s.id_типа_обучения = t.id_типа 
                WHERE n.название = 'Прикладная Информатика' AND t.название = 'Очная' 
                ORDER BY средний_балл DESC LIMIT 5""")

# 7. Однофамильцы 
process_data("7. Однофамильцы", "query_7_surnames", 
             "SELECT фамилия, COUNT(*) AS кол_во FROM студенты GROUP BY фамилия HAVING COUNT(*) > 1")

# 8. Полные тезки
process_data("8. Полные тезки", "query_8_full_names", 
             "SELECT фамилия, имя, отчество, COUNT(*) AS кол_во FROM студенты GROUP BY фамилия, имя, отчество HAVING COUNT(*) > 1")

conn.close()
print("\n" + "="*50)
print("Все файлы для отчета готовы в папке 'db_report'")