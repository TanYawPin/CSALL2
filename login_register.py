import tkinter as tk
from tkinter import messagebox
import sqlite3
from homepage import HomePage

class TourismSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Tourism System")
        root.geometry("700x500") 

        # Initialize database
        self.init_database()

        # GUI components
        self.label_username = tk.Label(self.root, text="Username:")
        self.label_username.pack()
        self.entry_username = tk.Entry(self.root)
        self.entry_username.pack()

        self.label_password = tk.Label(self.root, text="Password:")
        self.label_password.pack()
        self.entry_password = tk.Entry(self.root, show="*")
        self.entry_password.pack()

        self.register_button = tk.Button(self.root, text="Register", command=self.register_user)
        self.register_button.pack()

        self.login_button = tk.Button(self.root, text="Login", command=self.login_user)
        self.login_button.pack()

    def init_database(self):
        # Connect to SQLite database (create if not exists)
        self.conn = sqlite3.connect('tourism_database.db')
        self.create_user_table()

    def create_user_table(self):
        # Create user table if not exists
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    password TEXT,
                    is_admin INTEGER DEFAULT 0
                )
            ''')

    def register_user(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        with self.conn:
            cursor = self.conn.cursor()

            # Check if this is the first user (admin)
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]

            if count == 0:
                # This is the first user, set as admin
                cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", (username, password, 1))
            else:
                # Non-admin users are 0 by default
                cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", (username, password, 0))

        messagebox.showinfo("Registration", "Registration successful!")

    def login_user(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = cursor.fetchone()

        if user:
            # Check if the user is an admin
            is_admin = user[0] == 1 # Assuming is_admin is in the first position (index 0) in the tuple

            messagebox.showinfo("Login", "Login successful!")
            self.open_homepage(username, is_admin)  # Pass the username and admin status to the homepage
            self.root.destroy()  # Close the current login window
        else:
            messagebox.showerror("Login", "Invalid username or password")

    def open_homepage(self, username, is_admin):
        # Hide or destroy login/register buttons
        self.label_username.pack_forget()
        self.entry_username.pack_forget()
        self.label_password.pack_forget()
        self.entry_password.pack_forget()
        self.register_button.pack_forget()
        self.login_button.pack_forget()

        homepage = HomePage(self.root, username, is_admin)
        homepage.grab_set() 
        self.root.wait_window(homepage)

if __name__ == "__main__":
    root = tk.Tk()
    app = TourismSystem(root)
    root.mainloop()
