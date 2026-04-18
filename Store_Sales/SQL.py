import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class AdvancedShopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система управления торговлей v3.1")
        self.root.geometry("1000x750")
        
        self.init_db()
        self.create_widgets()

    def init_db(self):
        self.conn = sqlite3.connect('shop_manager.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Схема БД согласно ТЗ
        self.cursor.executescript('''
        CREATE TABLE IF NOT EXISTS categories (
            id_category INTEGER PRIMARY KEY AUTOINCREMENT,
            name_category TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS products (
            id_product INTEGER PRIMARY KEY AUTOINCREMENT,
            name_product TEXT NOT NULL,
            price REAL NOT NULL,
            id_category INTEGER NOT NULL,
            quantity_at_storage REAL NOT NULL CHECK(quantity_at_storage >= 0),
            FOREIGN KEY(id_category) REFERENCES categories(id_category)
        );

        CREATE TABLE IF NOT EXISTS receipts (
            id_check INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at DATE DEFAULT (DATE('now'))
        );

        CREATE TABLE IF NOT EXISTS sale_items (
            id_sale INTEGER PRIMARY KEY AUTOINCREMENT,
            id_check INTEGER NOT NULL,
            id_product INTEGER NOT NULL,
            quantity REAL NOT NULL,
            price_at_sale REAL NOT NULL,
            FOREIGN KEY(id_check) REFERENCES receipts(id_check),
            FOREIGN KEY(id_product) REFERENCES products(id_product)
        );
        ''')
        
        # Проверка и заполнение расширенным списком продуктов
        self.cursor.execute("SELECT COUNT(*) FROM categories")
        if self.cursor.fetchone()[0] == 0:
            # 1. Категории
            categories = [
                ('Компьютеры',), ('Смартфоны',), ('Периферия',), 
                ('Расходные материалы',), ('Сетевое оборудование',), ('Оргтехника',)
            ]
            self.cursor.executemany("INSERT INTO categories (name_category) VALUES (?)", categories)

            # 2. Расширенный список продуктов (Название, Цена, ID категории, Кол-во)
            products = [
                ('Ноутбук бизнес-серии', 95000, 1, 5),
                ('Игровой ПК (Base)', 72000, 1, 3),
                ('iPhone 15 Pro Max', 145000, 2, 4),
                ('Samsung Galaxy S24', 98000, 2, 6),
                ('Монитор 24" Full HD', 12500, 3, 10),
                ('Механическая клавиатура', 5500, 3, 15),
                ('Беспроводная мышь', 2400, 3, 25),
                ('Бумага А4 (коробка)', 2800, 4, 40),
                ('Набор картриджей', 8500, 4, 12),
                ('Wi-Fi 6 Роутер', 6800, 5, 8),
                ('Сетевой коммутатор', 4200, 5, 5),
                ('Лазерное МФУ', 24500, 6, 4),
                ('Планшет 10"', 35000, 2, 7)
            ]
            self.cursor.executemany(
                "INSERT INTO products (name_product, price, id_category, quantity_at_storage) VALUES (?, ?, ?, ?)", 
                products
            )
            
        self.conn.commit()

    def create_widgets(self):
        self.nb = ttk.Notebook(self.root)
        
        self.shop_frame = ttk.Frame(self.nb)
        self.setup_shop_tab()
        
        self.stats_frame = ttk.Frame(self.nb)
        self.setup_stats_tab()
        
        self.nb.add(self.shop_frame, text="🛒 Торговый зал")
        self.nb.add(self.stats_frame, text="📊 Отчеты и выручка")
        self.nb.pack(expand=True, fill='both')

    def setup_shop_tab(self):
        form = ttk.LabelFrame(self.shop_frame, text=" Новая продажа ")
        form.pack(side='left', padx=15, pady=15, fill='y')

        ttk.Label(form, text="Выберите товар:").pack(pady=5)
        self.prod_cb = ttk.Combobox(form, state="readonly", width=30)
        self.refresh_products()
        self.prod_cb.pack(pady=5, padx=10)

        ttk.Label(form, text="Количество:").pack(pady=5)
        self.qty_spin = ttk.Spinbox(form, from_=1, to=1000, width=12)
        self.qty_spin.set(1)
        self.qty_spin.pack(pady=5)

        ttk.Button(form, text="Подтвердить покупку", command=self.make_sale).pack(pady=25)

        right_panel = ttk.Frame(self.shop_frame)
        right_panel.pack(side='right', expand=True, fill='both', padx=15, pady=15)
        
        ttk.Label(right_panel, text="Состояние склада", font=('Segoe UI', 11, 'bold')).pack(pady=5)
        self.stock_tree = ttk.Treeview(right_panel, columns=("id", "name", "price", "qty"), show='headings')
        for c, h in zip(self.stock_tree["columns"], ["ID", "Название", "Цена (руб)", "Остаток"]):
            self.stock_tree.heading(c, text=h)
            self.stock_tree.column(c, width=90)
        self.stock_tree.pack(expand=True, fill='both')
        self.update_stock_table()

    def setup_stats_tab(self):
        top = ttk.Frame(self.stats_frame)
        top.pack(fill='x', padx=15, pady=15)

        ttk.Label(top, text="Дата (ГГГГ-ММ-ДД):").pack(side='left')
        self.date_entry = ttk.Entry(top, width=15)
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.date_entry.pack(side='left', padx=10)
        
        ttk.Button(top, text="Сформировать отчет", command=self.update_stats).pack(side='left', padx=5)

        self.summary_label = ttk.Label(self.stats_frame, text="Выручка за указанную дату: 0.00 руб.", font=('Segoe UI', 12, 'bold'))
        self.summary_label.pack(pady=10)

        self.sales_tree = ttk.Treeview(self.stats_frame, columns=("name", "total_qty", "revenue"), show='headings')
        self.sales_tree.heading("name", text="Наименование товара")
        self.sales_tree.heading("total_qty", text="Кол-во продано")
        self.sales_tree.heading("revenue", text="Итоговая выручка")
        self.sales_tree.pack(expand=True, fill='both', padx=15, pady=10)

    def refresh_products(self):
        self.cursor.execute("SELECT name_product FROM products WHERE quantity_at_storage > 0")
        self.prod_cb['values'] = [r[0] for r in self.cursor.fetchall()]

    def update_stock_table(self):
        for i in self.stock_tree.get_children(): self.stock_tree.delete(i)
        self.cursor.execute("SELECT id_product, name_product, price, quantity_at_storage FROM products")
        for row in self.cursor.fetchall(): self.stock_tree.insert("", "end", values=row)

    def make_sale(self):
        name = self.prod_cb.get()
        try:
            qty = float(self.qty_spin.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число")
            return

        if not name: 
            messagebox.showwarning("Внимание", "Выберите товар из списка")
            return

        self.cursor.execute("SELECT id_product, price, quantity_at_storage FROM products WHERE name_product=?", (name,))
        pid, price, stock = self.cursor.fetchone()

        if stock < qty:
            messagebox.showerror("Склад", f"Недостаточно товара! Доступно: {int(stock)} шт.")
            return

        try:
            # ТЗ: Отражение даты и id чека
            self.cursor.execute("INSERT INTO receipts (created_at) VALUES (DATE('now'))")
            check_id = self.cursor.lastrowid
            
            # ТЗ: Перечень купленного и расчет стоимости
            self.cursor.execute("INSERT INTO sale_items (id_check, id_product, quantity, price_at_sale) VALUES (?, ?, ?, ?)", 
                               (check_id, pid, qty, price))
            
            # ТЗ: Обновление количества на складе
            self.cursor.execute("UPDATE products SET quantity_at_storage = quantity_at_storage - ? WHERE id_product = ?", (qty, pid))
            
            self.conn.commit()
            messagebox.showinfo("Чек сформирован", f"ID чека: {check_id}\nСумма покупки: {qty*price:.2f} руб.")
            self.update_stock_table()
            self.refresh_products()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Ошибка системы", str(e))

    def update_stats(self):
        target_date = self.date_entry.get()
        for i in self.sales_tree.get_children(): self.sales_tree.delete(i)
        
        # ТЗ: Количество каждого проданного товара и выручка за выбранную дату
        query = '''
            SELECT 
                p.name_product, 
                SUM(si.quantity), 
                SUM(si.quantity * si.price_at_sale)
            FROM sale_items si
            JOIN receipts r ON si.id_check = r.id_check
            JOIN products p ON si.id_product = p.id_product
            WHERE r.created_at = ?
            GROUP BY p.name_product
        '''
        self.cursor.execute(query, (target_date,))
        rows = self.cursor.fetchall()
        
        total_day_revenue = 0
        for row in rows:
            self.sales_tree.insert("", "end", values=row)
            total_day_revenue += row[2]
        
        self.summary_label.config(text=f"Выручка за {target_date}: {total_day_revenue:.2f} руб.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedShopApp(root)
    root.mainloop()