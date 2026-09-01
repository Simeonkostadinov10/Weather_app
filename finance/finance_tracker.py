from datetime import datetime
import sqlite3
from tkinter import messagebox
import customtkinter as ctk

DB_NAME = "finance.db"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trans_type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL
            )
        """
        )
        conn.commit()


def add_transaction(trans_type, category, amount):
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO transactions (trans_type, category, amount, date)
            VALUES (?, ?, ?, ?)
        """,
            (trans_type, category, amount, date_str),
        )
        conn.commit()


def get_all_transactions():
    """Връща всички трансакции, подредени от най-новите към най-старите."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions ORDER BY id DESC")
        return cursor.fetchall()


def get_balance():
    """Изчислява общия баланс: Приходи минус Разходи."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT trans_type, SUM(amount) FROM transactions GROUP BY trans_type"
        )
        rows = cursor.fetchall()

        income = 0.0
        expense = 0.0
        for trans_type, total in rows:
            if trans_type == "Приход":
                income = total or 0.0
            elif trans_type == "Разход":
                expense = total or 0.0

        return income - expense


def delete_transaction(trans_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (trans_id,))
        conn.commit()


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class FinanceTrackerApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        init_db()

        self.title("Finance Tracker")
        self.geometry("520x650")
        self.resizable(True, True)

        self.balance_frame = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=12)
        self.balance_frame.pack(padx=20, pady=(20, 10), fill="x")

        self.balance_title = ctk.CTkLabel(
            self.balance_frame,
            text="Текущ баланс",
            font=("Arial", 14),
            text_color="#aaaaaa",
        )
        self.balance_title.pack(pady=(12, 0))

        self.balance_label = ctk.CTkLabel(
            self.balance_frame,
            text="0.00 EU.",
            font=("Arial", 28, "bold"),
            text_color="#2ecc71",
        )
        self.balance_label.pack(pady=(0, 12))

        # 2. Форма за добавяне на трансакция
        self.input_frame = ctk.CTkFrame(self, fg_color="#181818", corner_radius=12)
        self.input_frame.pack(padx=20, pady=10, fill="x")

        # Избор тип: Приход / Разход
        self.type_selector = ctk.CTkSegmentedButton(
            self.input_frame,
            values=["Разход", "Приход"],
            selected_color="#3498db",
            selected_hover_color="#2980b9",
        )
        self.type_selector.set("Разход")
        self.type_selector.pack(padx=15, pady=(15, 10), fill="x")

        # Избор на категория
        self.categories = [
            "Храна",
            "Сметки / Наем",
            "Транспорт",
            "Забавления",
            "Заплата",
            "Инвестиции",
            "Други",
        ]
        self.category_dropdown = ctk.CTkComboBox(
            self.input_frame,
            values=self.categories,
            width=200,
            dropdown_hover_color="#333333",
        )
        self.category_dropdown.set("Храна")
        self.category_dropdown.pack(padx=15, pady=12, fill="x")

        self.amount_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Въведи сума (напр. 25.50)",
            height=38,
        )
        self.amount_entry.pack(padx=15, pady=12, fill="x")

        # Бутон за добавяне
        self.add_btn = ctk.CTkButton(
            self.input_frame,
            text="+ Добави запис",
            command=self.handle_add_transaction,
            height=38,
            fg_color="#27ae60",
            hover_color="#219150",
            font=("Arial", 14, "bold"),
        )
        self.add_btn.pack(padx=15, pady=(5, 15), fill="x")

        # Enter клавиш за бързо добавяне
        self.bind("<Return>", lambda event: self.handle_add_transaction())

        # 3. Списък с последни трансакции
        self.list_title = ctk.CTkLabel(
            self,
            text="История на трансакциите",
            font=("Arial", 15, "bold"),
            text_color="white",
        )
        self.list_title.pack(padx=20, pady=(10, 5), anchor="w")

        self.transactions_frame = ctk.CTkScrollableFrame(
            self, height=220, fg_color="#181818", corner_radius=10
        )
        self.transactions_frame.pack(padx=20, pady=(0, 20), fill="both", expand=True)

        self.refresh_ui()

    def handle_add_transaction(self):
        """Валидира входа и записва новата трансакция."""
        amount_text = self.amount_entry.get().strip().replace(",", ".")
        trans_type = self.type_selector.get()
        category = self.category_dropdown.get().strip()

        if not amount_text:
            messagebox.showerror("Грешка", "Моля, въведи сума!")
            return

        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Невалидна сума", "Сумата трябва да е положително число!"
            )
            return

        # Запис в базата данни
        add_transaction(trans_type, category, amount)

        # Изчистване на полето и обновяване на интерфейса
        self.amount_entry.delete(0, "end")
        self.refresh_ui()

    def handle_delete_transaction(self, trans_id):
        """Изтрива конкретна трансакция и презарежда екрана."""
        delete_transaction(trans_id)
        self.refresh_ui()

    def refresh_ui(self):
        balance = get_balance()
        if balance >= 0:
            self.balance_label.configure(
                text=f"+{balance:.2f} eu.", text_color="#2ecc71"
            )
        else:
            self.balance_label.configure(
                text=f"{balance:.2f} eu.", text_color="#e74c3c"
            )

        # 2. Изчистване на старите редове в списъка
        for widget in self.transactions_frame.winfo_children():
            widget.destroy()

        # 3. Зареждане на новите редове
        transactions = get_all_transactions()
        if not transactions:
            empty_lbl = ctk.CTkLabel(
                self.transactions_frame,
                text="Все още няма добавени трансакции.",
                text_color="#666666",
            )
            empty_lbl.pack(pady=30)
            return

        for trans_id, trans_type, category, amount, date_str in transactions:
            amount_val = float(amount)
            row = ctk.CTkFrame(
                self.transactions_frame, fg_color="#222222", corner_radius=8
            )
            row.pack(fill="x", padx=5, pady=4)

            # Цвят и знак според типа
            if trans_type == "Приход":
                amount_color = "#2ecc71"
                amount_display = f"+{amount_val:.2f} EU."
            else:
                amount_color = "#e74c3c"
                amount_display = f"-{amount_val:.2f} EU."

            # Лява част: Категория и дата
            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.pack(side="left", padx=10, pady=6)

            cat_lbl = ctk.CTkLabel(
                info_frame,
                text=category,
                font=("Arial", 13, "bold"),
                text_color="white",
            )
            cat_lbl.pack(anchor="w")

            date_lbl = ctk.CTkLabel(
                info_frame,
                text=date_str,
                font=("Arial", 10),
                text_color="#777777",
            )
            date_lbl.pack(anchor="w")

            # Дясна част: Бутон за изтриване (X)
            del_btn = ctk.CTkButton(
                row,
                text="✕",
                width=28,
                height=28,
                fg_color="#333333",
                hover_color="#c0392b",
                text_color="#ffffff",
                command=lambda t_id=trans_id: self.handle_delete_transaction(t_id),
            )
            del_btn.pack(side="right", padx=10, pady=6)

            # Дясна част: Сума
            amount_lbl = ctk.CTkLabel(
                row,
                text=amount_display,
                font=("Arial", 14, "bold"),
                text_color=amount_color,
            )
            amount_lbl.pack(side="right", padx=12, pady=6)


if __name__ == "__main__":
    app = FinanceTrackerApp()
    app.mainloop()