import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import Style
from tkinter import ttk
import sqlite3
from os.path import exists
import matplotlib.pyplot as plt  # Importing matplotlib for plotting

class ExpenseTracker(tk.Tk):
    def __init__(self):
        super().__init__()

        style = Style(theme="darkly")
        style.configure("Treeview", rowheight=25)

        self.configure(bg="#222222")

        self.title("Expense Tracker")
        self.geometry("600x500")
        self.resizable(False, False)

        self.db_file = "expenses.db"
        self.create_database()
        self.load_expenses()

        self.create_widgets()

    def create_database(self):
        if not exists(self.db_file):
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute(
                """CREATE TABLE expenses
                         (date text, category text, amount real)"""
            )
            conn.commit()
            conn.close()

    def load_expenses(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT * FROM expenses")
        self.expenses = c.fetchall()
        conn.close()

    def save_expense(self, date, category, amount):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("INSERT INTO expenses VALUES (?, ?, ?)", (date, category, amount))
        conn.commit()
        conn.close()

    def update_expense(
        self, old_date, old_category, old_amount, new_date, new_category, new_amount
    ):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute(
            "UPDATE expenses SET date=?, category=?, amount=? WHERE date=? AND category=? AND amount=?",
            (new_date, new_category, new_amount, old_date, old_category, old_amount),
        )
        conn.commit()
        conn.close()

    def delete_expense(self):
        item = self.tree_expenses.selection()[0]
        values = self.tree_expenses.item(item, "values")
        if values:
            confirm = messagebox.askyesno(
                "Confirm Delete", "Are you sure you want to delete this expense?"
            )
            if confirm:
                conn = sqlite3.connect(self.db_file)
                c = conn.cursor()
                c.execute(
                    "DELETE FROM expenses WHERE date=? AND category=? AND amount=?",
                    values,
                )
                conn.commit()
                conn.close()
                self.load_expenses()
                self.update_expenses()
        else:
            messagebox.showwarning("Warning", "Please select an expense to delete.")

    def edit_expense(self):
        item = self.tree_expenses.selection()[0]
        values = self.tree_expenses.item(item, "values")
        if values:
            old_date, old_category, old_amount = values

            # Fill entries with existing values for editing
            self.entry_date.delete(0, tk.END)
            self.entry_date.insert(0, old_date)
            self.entry_category.delete(0, tk.END)
            self.entry_category.insert(0, old_category)
            self.entry_amount.delete(0, tk.END)
            self.entry_amount.insert(0, old_amount)

            # Add an "Update" button
            self.button_update_expense = ttk.Button(
                self,
                text="Update Expense",
                bootstyle="warning",
                command=lambda: self.update_expense_in_db(
                    old_date, old_category, old_amount
                ),
            )
            self.button_update_expense.grid(row=3, columnspan=2, pady=10)
            self.button_update_expense.config(cursor="hand2")

        else:
            messagebox.showwarning("Warning", "Please select an expense to edit.")

    def update_expense_in_db(self, old_date, old_category, old_amount):
        new_date = self.entry_date.get()
        new_category = self.entry_category.get()
        new_amount = self.entry_amount.get()

        if new_date and new_category and new_amount:
            self.update_expense(
                old_date, old_category, old_amount, new_date, new_category, new_amount
            )
            self.load_expenses()
            self.update_expenses()
            self.entry_date.delete(0, tk.END)
            self.entry_category.delete(0, tk.END)
            self.entry_amount.delete(0, tk.END)
            self.button_update_expense.grid_forget()  # Remove the update button after the update
        else:
            messagebox.showwarning("Warning", "Please enter all fields.")

    def create_widgets(self):
        label_style = {"font": ("Helvetica", 12, "bold"), "foreground": "#4ECCA3"}

        # Entry Styles
        entry_style = {"bootstyle": "info", "width": 25}

        # Date input
        self.label_date = ttk.Label(self, text="Date:", **label_style)
        self.label_date.grid(row=0, column=0, padx=20, pady=10, sticky="e")
        self.entry_date = ttk.Entry(self, **entry_style)
        self.entry_date.grid(row=0, column=1, padx=20, pady=10)

        # Category input
        self.label_category = ttk.Label(self, text="Category:", **label_style)
        self.label_category.grid(row=1, column=0, padx=20, pady=10, sticky="e")
        self.entry_category = ttk.Entry(self, **entry_style)
        self.entry_category.grid(row=1, column=1, padx=20, pady=10)

        # Amount input
        self.label_amount = ttk.Label(self, text="Amount:", **label_style)
        self.label_amount.grid(row=2, column=0, padx=20, pady=10, sticky="e")
        self.entry_amount = ttk.Entry(self, **entry_style)
        self.entry_amount.grid(row=2, column=1, padx=20, pady=10)

        # Buttons (Purple primary action color)
        self.button_add_expense = ttk.Button(
            self,
            text="Add Expense",
            bootstyle="primary",
            command=self.add_expense,
            style="primary.TButton",
        )
        self.button_add_expense.grid(row=3, columnspan=2, pady=10)
        self.button_add_expense.config(cursor="hand2")

        # Visualization Button
        self.button_visualize_expenses = ttk.Button(
            self,
            text="Visualize Expenses",
            bootstyle="info",
            command=self.visualize_expenses,
            style="info.TButton",
        )
        self.button_visualize_expenses.grid(row=4, columnspan=2, pady=10)
        self.button_visualize_expenses.config(cursor="hand2")

        # Treeview for displaying expenses
        self.tree_expenses = ttk.Treeview(
            self, columns=("Date", "Category", "Amount"), show="headings", height=10
        )
        self.tree_expenses.heading("Date", text="Date")
        self.tree_expenses.heading("Category", text="Category")
        self.tree_expenses.heading("Amount", text="Amount")
        self.tree_expenses.column("Date", width=100)
        self.tree_expenses.column("Category", width=150)
        self.tree_expenses.column("Amount", width=100)
        self.tree_expenses.grid(row=5, columnspan=2, padx=10, pady=20)
        self.tree_expenses.bind("<Button-1>", self.on_treeview_click)

        # Total Expenses Label (Teal for highlighting totals)
        self.label_total = ttk.Label(
            self,
            text="Total Expenses: $0.00",
            font=("Helvetica", 14),
            foreground="#4ECCA3",
        )
        self.label_total.grid(row=6, columnspan=2, pady=10)

        # Context menu for deleting and editing expenses
        self.create_context_menu()

        # Update the expenses in the UI
        self.update_expenses()

    def visualize_expenses(self):
        # Group expenses by category for plotting
        category_totals = {}
        for expense in self.expenses:
            category = expense[1]
            amount = float(expense[2])
            category_totals[category] = category_totals.get(category, 0) + amount

        categories = list(category_totals.keys())
        amounts = list(category_totals.values())

        # Create a pie chart or bar chart (you can choose which one you prefer)
        plt.figure(figsize=(6, 6))
        plt.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=90)
        plt.title("Expenses by Category")
        plt.axis("equal")  # Equal aspect ratio ensures the pie is drawn as a circle.
        plt.show()

    def add_expense(self):
        date = self.entry_date.get()
        category = self.entry_category.get()
        amount = self.entry_amount.get()

        if date and category and amount:
            self.save_expense(date, category, amount)
            self.load_expenses()
            self.update_expenses()
            self.entry_date.delete(0, tk.END)
            self.entry_category.delete(0, tk.END)
            self.entry_amount.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Please enter all fields.")

    def on_treeview_click(self, event):
        pass  # You can implement this if you need row-specific actions

    def update_expenses(self):
        # Clear the treeview
        for item in self.tree_expenses.get_children():
            self.tree_expenses.delete(item)

        # Add all expenses to the treeview
        total = 0
        for expense in self.expenses:
            self.tree_expenses.insert("", tk.END, values=expense)
            total += float(expense[2])

        # Update the total label
        self.label_total.config(text=f"Total Expenses: ${total:.2f}")

    def create_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(
            label="Edit Expense", command=self.edit_expense, foreground="#FFD700"
        )
        self.context_menu.add_command(
            label="Delete Expense", command=self.delete_expense, foreground="#FF6347"
        )

        # Bind right-click to show the context menu
        self.tree_expenses.bind(
            "<Button-3>",
            lambda event: self.context_menu.post(event.x_root, event.y_root),
        )


if __name__ == "__main__":
    app = ExpenseTracker()
    app.mainloop()
