import sqlite3

conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Создание таблиц согласно схеме 
cursor.executescript('''
CREATE TABLE уровень_обучения (
    id_уровня INTEGER PRIMARY KEY,
    название VARCHAR(100)
);

CREATE TABLE направления (
    id_направления INTEGER PRIMARY KEY,
    название VARCHAR(100)
);

CREATE TABLE типы_обучения (
    id_типа INTEGER PRIMARY KEY,
    название VARCHAR(100)
);

CREATE TABLE студенты (
    id_студента INTEGER PRIMARY KEY,
    id_уровня INTEGER,
    id_направления INTEGER,
    id_типа_обучения INTEGER,
    фамилия VARCHAR(100),
    имя VARCHAR(100),
    отчество VARCHAR(100),
    средний_балл INTEGER,
    FOREIGN KEY (id_уровня) REFERENCES уровень_обучения(id_уровня),
    FOREIGN KEY (id_направления) REFERENCES направления(id_направления),
    FOREIGN KEY (id_типа_обучения) REFERENCES типы_обучения(id_типа)
);

-- Наполнение справочников 
INSERT INTO уровень_обучения VALUES (1, 'Бакалавриат'), (2, 'Магистратура'), (3, 'Аспирантура');
INSERT INTO направления VALUES (1, 'Прикладная математика'), (2, 'Информационные системы'), (3, 'Экономика'), (4, 'Юриспруденция');
INSERT INTO типы_обучения VALUES (1, 'Бюджет'), (2, 'Контракт'), (3, 'Целевое');

-- Добавляем большой массив данных о студентах 
INSERT INTO студенты (id_студента, id_уровня, id_направления, id_типа_обучения, фамилия, имя, средний_балл)
VALUES 
(1, 1, 1, 1, 'Иванов', 'Иван', 98),
(2, 1, 1, 2, 'Петров', 'Петр', 72),
(3, 2, 2, 1, 'Сидорова', 'Анна', 85),
(4, 1, 2, 2, 'Кузнецов', 'Алексей', 45),
(5, 1, 3, 1, 'Смирнова', 'Мария', 91),
(6, 2, 3, 2, 'Попов', 'Дмитрий', 64),
(7, 3, 1, 3, 'Васильев', 'Артем', 100),
(8, 1, 4, 1, 'Соколов', 'Игорь', 88),
(9, 2, 4, 2, 'Михайлов', 'Михаил', 55),
(10, 1, 2, 1, 'Новикова', 'Елена', 79),
(11, 2, 1, 1, 'Федоров', 'Олег', 93),
(12, 1, 3, 2, 'Морозов', 'Степан', 38),
(13, 3, 2, 3, 'Волков', 'Владимир', 96),
(14, 1, 4, 1, 'Лебедев', 'Денис', 82),
(15, 2, 3, 1, 'Семенов', 'Кирилл', 75);
''')

def run_query(title, query):
    print(f"\n{title}")
    cursor.execute(query)
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    print(f"{' | '.join(f'{name:<20}' for name in colnames)}")
    print("-" * (23 * len(colnames)))
    for row in rows:
        print(f"{' | '.join(f'{str(item):<20}' for item in row)}")

# ЗАДАНИЕ 1: Запросы с CASE
query_case = '''
SELECT 
    фамилия, 
    средний_балл,
    CASE 
        WHEN средний_балл >= 90 THEN 'Отличник'
        WHEN средний_балл >= 75 THEN 'Хорошист'
        WHEN средний_балл >= 60 THEN 'Удовл.'
        ELSE 'Неудовл.'
    END as статус
FROM студенты
ORDER BY средний_балл DESC;
'''
run_query("ЗАДАНИЕ 1: Классификация студентов (CASE)", query_case)

# ЗАДАНИЕ 2: Запросы с подзапросами
query_subquery = '''
SELECT фамилия, средний_балл
FROM студенты
WHERE id_направления IN (
    SELECT id_направления 
    FROM направления 
    WHERE название LIKE '%Информационные%'
) AND средний_балл > (SELECT AVG(средний_балл) FROM студенты);
'''
run_query("ЗАДАНИЕ 2: Лучшие IT-специалисты (Подзапрос)", query_subquery)

# ЗАДАНИЕ 3: Запросы с CTE
query_cte = '''
WITH СтатистикаПоУровням AS (
    SELECT 
        id_уровня, 
        COUNT(*) as студентов,
        ROUND(AVG(средний_балл), 2) as средний_балл_уровня,
        MAX(средний_балл) as лучший_результат
    FROM студенты
    GROUP BY id_уровня
)
SELECT 
    u.название as уровень, 
    s.студентов, 
    s.средний_балл_уровня,
    s.лучший_результат
FROM СтатистикаПоУровням s
JOIN уровень_обучения u ON s.id_уровня = u.id_уровня
ORDER BY s.средний_балл_уровня DESC;
'''
run_query("ЗАДАНИЕ 3: Аналитика по уровням обучения (CTE)", query_cte)

conn.close()
