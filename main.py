import tkinter as tk
from tkinter import messagebox, tkk
import sqlite3
from os.path import exists
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.cm as cm
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors as reportlab_colors
from reportlab.platypus import Spacer
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.platypus.flowables import Image as PlatypusImage
from reportlab.pdfgen import canvas
import io


class ExpenseTracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker")

        self.db_file = "expense.db"
        self.create_database()
        self.load_expenses()
        self.create_widgets()
        self.create_context_menu()

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
        if not exists(self.db_file):
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("""SELECT * FROM expenses""")
            self.expenses = c.fetchall()
            conn.close()

            self.expenses = [
                (date, category, float(amount))
                for date, category, amount in self.expenses
            ]
